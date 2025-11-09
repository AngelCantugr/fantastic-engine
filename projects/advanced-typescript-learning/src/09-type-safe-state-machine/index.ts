/**
 * 09 - Type-Safe State Machine
 *
 * Finite State Machine with compile-time guarantees using TypeScript
 */

// ============================================================================
// PART 1: BASIC STATE MACHINE TYPES
// ============================================================================

/**
 * State machine configuration
 */
export type StateMachineConfig<
  States extends string,
  Events extends string
> = {
  initial: States;
  states: {
    [K in States]: {
      on?: {
        [E in Events]?: States;
      };
      entry?: () => void;
      exit?: () => void;
    };
  };
};

/**
 * State machine instance
 */
export class StateMachine<
  States extends string,
  Events extends string
> {
  private currentState: States;
  private config: StateMachineConfig<States, Events>;
  private listeners: Set<(state: States) => void> = new Set();

  constructor(config: StateMachineConfig<States, Events>) {
    this.config = config;
    this.currentState = config.initial;
    this.config.states[this.currentState].entry?.();
  }

  get state(): States {
    return this.currentState;
  }

  send(event: Events): void {
    const currentStateConfig = this.config.states[this.currentState];
    const nextState = currentStateConfig.on?.[event];

    if (nextState) {
      this.transition(nextState);
    }
  }

  private transition(nextState: States): void {
    const prevState = this.currentState;

    // Exit previous state
    this.config.states[prevState].exit?.();

    // Update state
    this.currentState = nextState;

    // Enter new state
    this.config.states[nextState].entry?.();

    // Notify listeners
    this.listeners.forEach((listener) => listener(nextState));
  }

  onTransition(listener: (state: States) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

// ============================================================================
// PART 2: TYPED STATE MACHINE
// ============================================================================

/**
 * State machine with context (extended state)
 */
export type TypedStateMachineConfig<
  States extends string,
  Events extends string,
  Context = {}
> = {
  initial: States;
  context: Context;
  states: {
    [K in States]: {
      on?: {
        [E in Events]?: {
          target: States;
          guard?: (context: Context) => boolean;
          action?: (context: Context) => Context;
        };
      };
      entry?: (context: Context) => void;
      exit?: (context: Context) => void;
    };
  };
};

export class TypedStateMachine<
  States extends string,
  Events extends string,
  Context = {}
> {
  private currentState: States;
  private context: Context;
  private config: TypedStateMachineConfig<States, Events, Context>;
  private listeners: Set<(state: States, context: Context) => void> = new Set();

  constructor(config: TypedStateMachineConfig<States, Events, Context>) {
    this.config = config;
    this.currentState = config.initial;
    this.context = config.context;
    this.config.states[this.currentState].entry?.(this.context);
  }

  get state(): States {
    return this.currentState;
  }

  get value(): Context {
    return this.context;
  }

  send(event: Events): void {
    const currentStateConfig = this.config.states[this.currentState];
    const transition = currentStateConfig.on?.[event];

    if (transition) {
      // Check guard condition
      if (transition.guard && !transition.guard(this.context)) {
        return;
      }

      // Execute action and update context
      if (transition.action) {
        this.context = transition.action(this.context);
      }

      // Perform transition
      this.transition(transition.target);
    }
  }

  private transition(nextState: States): void {
    const prevState = this.currentState;

    // Exit previous state
    this.config.states[prevState].exit?.(this.context);

    // Update state
    this.currentState = nextState;

    // Enter new state
    this.config.states[nextState].entry?.(this.context);

    // Notify listeners
    this.listeners.forEach((listener) => listener(nextState, this.context));
  }

  onTransition(listener: (state: States, context: Context) => void): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }
}

// ============================================================================
// PART 3: HIERARCHICAL STATE MACHINE
// ============================================================================

export type HierarchicalState<T extends string> = {
  name: T;
  parent?: T;
};

// ============================================================================
// EXAMPLE 1: TRAFFIC LIGHT
// ============================================================================

type TrafficStates = 'red' | 'yellow' | 'green';
type TrafficEvents = 'TIMER';

const trafficLight = new StateMachine<TrafficStates, TrafficEvents>({
  initial: 'red',
  states: {
    red: {
      on: { TIMER: 'green' },
      entry: () => console.log('🔴 Red light - STOP'),
    },
    yellow: {
      on: { TIMER: 'red' },
      entry: () => console.log('🟡 Yellow light - CAUTION'),
    },
    green: {
      on: { TIMER: 'yellow' },
      entry: () => console.log('🟢 Green light - GO'),
    },
  },
});

// ============================================================================
// EXAMPLE 2: DOOR
// ============================================================================

type DoorStates = 'closed' | 'opening' | 'open' | 'closing';
type DoorEvents = 'OPEN' | 'CLOSE' | 'COMPLETE';

const door = new StateMachine<DoorStates, DoorEvents>({
  initial: 'closed',
  states: {
    closed: {
      on: { OPEN: 'opening' },
      entry: () => console.log('Door is closed'),
    },
    opening: {
      on: { COMPLETE: 'open' },
      entry: () => console.log('Door is opening...'),
    },
    open: {
      on: { CLOSE: 'closing' },
      entry: () => console.log('Door is open'),
    },
    closing: {
      on: { COMPLETE: 'closed', OPEN: 'opening' },
      entry: () => console.log('Door is closing...'),
    },
  },
});

// ============================================================================
// EXAMPLE 3: PROMISE-LIKE STATE MACHINE
// ============================================================================

type PromiseStates = 'pending' | 'fulfilled' | 'rejected';
type PromiseEvents = 'RESOLVE' | 'REJECT';

interface PromiseContext<T> {
  value?: T;
  error?: Error;
}

const createPromiseStateMachine = <T>() =>
  new TypedStateMachine<PromiseStates, PromiseEvents, PromiseContext<T>>({
    initial: 'pending',
    context: {},
    states: {
      pending: {
        on: {
          RESOLVE: {
            target: 'fulfilled',
            action: (ctx) => ({ ...ctx, value: undefined as T }),
          },
          REJECT: {
            target: 'rejected',
            action: (ctx) => ({ ...ctx, error: new Error('Rejected') }),
          },
        },
      },
      fulfilled: {
        on: {},
        entry: (ctx) => console.log('Fulfilled with:', ctx.value),
      },
      rejected: {
        on: {},
        entry: (ctx) => console.log('Rejected with:', ctx.error),
      },
    },
  });

// ============================================================================
// EXAMPLE 4: AUTHENTICATION
// ============================================================================

type AuthStates = 'loggedOut' | 'loggingIn' | 'loggedIn' | 'error';
type AuthEvents = 'LOGIN' | 'SUCCESS' | 'FAILURE' | 'LOGOUT';

interface AuthContext {
  userId?: number;
  username?: string;
  error?: string;
  attempts: number;
}

const authMachine = new TypedStateMachine<AuthStates, AuthEvents, AuthContext>({
  initial: 'loggedOut',
  context: {
    attempts: 0,
  },
  states: {
    loggedOut: {
      on: {
        LOGIN: {
          target: 'loggingIn',
          action: (ctx) => ({ ...ctx, attempts: ctx.attempts + 1 }),
        },
      },
      entry: () => console.log('Not authenticated'),
    },
    loggingIn: {
      on: {
        SUCCESS: {
          target: 'loggedIn',
          action: (ctx) => ({ ...ctx, attempts: 0 }),
        },
        FAILURE: {
          target: 'error',
          guard: (ctx) => ctx.attempts < 3,
          action: (ctx) => ({ ...ctx, error: 'Invalid credentials' }),
        },
      },
      entry: () => console.log('Authenticating...'),
    },
    loggedIn: {
      on: {
        LOGOUT: {
          target: 'loggedOut',
          action: () => ({ attempts: 0 }),
        },
      },
      entry: (ctx) => console.log('Logged in as:', ctx.username),
    },
    error: {
      on: {
        LOGIN: {
          target: 'loggingIn',
          guard: (ctx) => ctx.attempts < 3,
        },
      },
      entry: (ctx) => console.log('Error:', ctx.error),
    },
  },
});

// ============================================================================
// EXAMPLE 5: FETCH STATE MACHINE
// ============================================================================

type FetchStates = 'idle' | 'loading' | 'success' | 'failure';
type FetchEvents = 'FETCH' | 'RESOLVE' | 'REJECT' | 'RETRY';

interface FetchContext<T> {
  data?: T;
  error?: string;
  retries: number;
}

function createFetchMachine<T>() {
  return new TypedStateMachine<FetchStates, FetchEvents, FetchContext<T>>({
    initial: 'idle',
    context: {
      retries: 0,
    },
    states: {
      idle: {
        on: {
          FETCH: {
            target: 'loading',
          },
        },
      },
      loading: {
        on: {
          RESOLVE: {
            target: 'success',
            action: (ctx) => ({ ...ctx, retries: 0 }),
          },
          REJECT: {
            target: 'failure',
            action: (ctx) => ({ ...ctx, retries: ctx.retries + 1 }),
          },
        },
        entry: () => console.log('Loading...'),
      },
      success: {
        on: {
          FETCH: {
            target: 'loading',
          },
        },
        entry: (ctx) => console.log('Success:', ctx.data),
      },
      failure: {
        on: {
          RETRY: {
            target: 'loading',
            guard: (ctx) => ctx.retries < 3,
          },
          FETCH: {
            target: 'loading',
          },
        },
        entry: (ctx) => console.log('Failed:', ctx.error),
      },
    },
  });
}

// ============================================================================
// TESTS
// ============================================================================

console.log('=== Traffic Light Test ===');
console.log('Current state:', trafficLight.state);
trafficLight.send('TIMER');
console.log('Current state:', trafficLight.state);
trafficLight.send('TIMER');
console.log('Current state:', trafficLight.state);

console.log('\n=== Door Test ===');
door.send('OPEN');
door.send('COMPLETE');
door.send('CLOSE');
door.send('COMPLETE');

console.log('\n=== Auth Test ===');
authMachine.send('LOGIN');
authMachine.send('FAILURE');
console.log('Auth context:', authMachine.value);

console.log('Type-Safe State Machine module loaded successfully!');
