/*!
 * Event Sourcing System
 * Features: Event store, projections, snapshots, replay
 */

use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use serde::{Deserialize, Serialize};
use chrono::{DateTime, Utc};

type AggregateId = String;
type EventId = u64;
type Version = u64;

/// Base event trait
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Event {
    id: EventId,
    aggregate_id: AggregateId,
    event_type: String,
    data: serde_json::Value,
    metadata: EventMetadata,
    version: Version,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct EventMetadata {
    timestamp: DateTime<Utc>,
    user_id: Option<String>,
    correlation_id: Option<String>,
}

/// Event store
struct EventStore {
    events: Vec<Event>,
    next_id: EventId,
    snapshots: HashMap<AggregateId, Snapshot>,
}

impl EventStore {
    fn new() -> Self {
        Self {
            events: Vec::new(),
            next_id: 1,
            snapshots: HashMap::new(),
        }
    }

    /// Append event to store
    fn append_event(
        &mut self,
        aggregate_id: AggregateId,
        event_type: String,
        data: serde_json::Value,
        expected_version: Option<Version>,
    ) -> Result<Event, String> {
        // Get current version
        let current_version = self.get_current_version(&aggregate_id);

        // Check optimistic locking
        if let Some(expected) = expected_version {
            if current_version != expected {
                return Err(format!(
                    "Version mismatch: expected {}, got {}",
                    expected, current_version
                ));
            }
        }

        let event = Event {
            id: self.next_id,
            aggregate_id: aggregate_id.clone(),
            event_type,
            data,
            metadata: EventMetadata {
                timestamp: Utc::now(),
                user_id: None,
                correlation_id: None,
            },
            version: current_version + 1,
        };

        self.events.push(event.clone());
        self.next_id += 1;

        log::info!(
            "Appended event {} for aggregate {} (version {})",
            event.id,
            aggregate_id,
            event.version
        );

        Ok(event)
    }

    /// Get events for aggregate
    fn get_events(
        &self,
        aggregate_id: &AggregateId,
        from_version: Option<Version>,
    ) -> Vec<Event> {
        self.events
            .iter()
            .filter(|e| {
                e.aggregate_id == *aggregate_id
                    && from_version.map_or(true, |v| e.version > v)
            })
            .cloned()
            .collect()
    }

    /// Get all events (for replay)
    fn get_all_events(&self) -> &[Event] {
        &self.events
    }

    /// Get current version of aggregate
    fn get_current_version(&self, aggregate_id: &AggregateId) -> Version {
        self.events
            .iter()
            .filter(|e| e.aggregate_id == *aggregate_id)
            .map(|e| e.version)
            .max()
            .unwrap_or(0)
    }

    /// Create snapshot
    fn create_snapshot(&mut self, aggregate_id: AggregateId, state: serde_json::Value) {
        let version = self.get_current_version(&aggregate_id);

        let snapshot = Snapshot {
            aggregate_id: aggregate_id.clone(),
            version,
            state,
            timestamp: Utc::now(),
        };

        self.snapshots.insert(aggregate_id, snapshot);
    }

    /// Get snapshot
    fn get_snapshot(&self, aggregate_id: &AggregateId) -> Option<&Snapshot> {
        self.snapshots.get(aggregate_id)
    }
}

/// Snapshot
#[derive(Debug, Clone, Serialize, Deserialize)]
struct Snapshot {
    aggregate_id: AggregateId,
    version: Version,
    state: serde_json::Value,
    timestamp: DateTime<Utc>,
}

/// Example: Bank Account Aggregate
#[derive(Debug, Clone, Serialize, Deserialize)]
struct BankAccount {
    id: AggregateId,
    balance: f64,
    version: Version,
}

impl BankAccount {
    fn new(id: AggregateId) -> Self {
        Self {
            id,
            balance: 0.0,
            version: 0,
        }
    }

    /// Apply event to state
    fn apply_event(&mut self, event: &Event) -> Result<(), String> {
        match event.event_type.as_str() {
            "AccountOpened" => {
                // Already initialized
                self.version = event.version;
                Ok(())
            }
            "MoneyDeposited" => {
                if let Some(amount) = event.data.get("amount").and_then(|a| a.as_f64()) {
                    self.balance += amount;
                    self.version = event.version;
                    Ok(())
                } else {
                    Err("Invalid deposit amount".to_string())
                }
            }
            "MoneyWithdrawn" => {
                if let Some(amount) = event.data.get("amount").and_then(|a| a.as_f64()) {
                    if self.balance >= amount {
                        self.balance -= amount;
                        self.version = event.version;
                        Ok(())
                    } else {
                        Err("Insufficient funds".to_string())
                    }
                } else {
                    Err("Invalid withdrawal amount".to_string())
                }
            }
            _ => Err(format!("Unknown event type: {}", event.event_type)),
        }
    }

    /// Rebuild state from events
    fn from_events(events: &[Event]) -> Result<Self, String> {
        let mut account = Self::new(events[0].aggregate_id.clone());

        for event in events {
            account.apply_event(event)?;
        }

        Ok(account)
    }

    /// Rebuild from snapshot + events
    fn from_snapshot_and_events(
        snapshot: &Snapshot,
        events: &[Event],
    ) -> Result<Self, String> {
        let mut account: BankAccount = serde_json::from_value(snapshot.state.clone())
            .map_err(|e| e.to_string())?;

        for event in events {
            account.apply_event(event)?;
        }

        Ok(account)
    }
}

#[tokio::main]
async fn main() {
    env_logger::init();

    log::info!("Starting event sourcing system");

    let event_store = Arc::new(RwLock::new(EventStore::new()));

    // Example: Bank account operations
    let account_id = "acc-123".to_string();

    // Open account
    {
        let mut store = event_store.write().await;
        store
            .append_event(
                account_id.clone(),
                "AccountOpened".to_string(),
                serde_json::json!({}),
                None,
            )
            .unwrap();
    }

    // Deposit money
    {
        let mut store = event_store.write().await;
        store
            .append_event(
                account_id.clone(),
                "MoneyDeposited".to_string(),
                serde_json::json!({ "amount": 100.0 }),
                Some(1),
            )
            .unwrap();

        store
            .append_event(
                account_id.clone(),
                "MoneyDeposited".to_string(),
                serde_json::json!({ "amount": 50.0 }),
                Some(2),
            )
            .unwrap();
    }

    // Withdraw money
    {
        let mut store = event_store.write().await;
        store
            .append_event(
                account_id.clone(),
                "MoneyWithdrawn".to_string(),
                serde_json::json!({ "amount": 30.0 }),
                Some(3),
            )
            .unwrap();
    }

    // Rebuild state from events
    {
        let store = event_store.read().await;
        let events = store.get_events(&account_id, None);
        let account = BankAccount::from_events(&events).unwrap();

        log::info!("Account state: {:?}", account);
        log::info!("Balance: ${:.2}", account.balance);
    }

    // Create snapshot
    {
        let mut store = event_store.write().await;
        let events = store.get_events(&account_id, None);
        let account = BankAccount::from_events(&events).unwrap();

        store.create_snapshot(account_id.clone(), serde_json::to_value(&account).unwrap());
        log::info!("Created snapshot at version {}", account.version);
    }

    // Replay from snapshot
    {
        let store = event_store.read().await;
        let snapshot = store.get_snapshot(&account_id).unwrap();
        let events = store.get_events(&account_id, Some(snapshot.version));
        let account = BankAccount::from_snapshot_and_events(snapshot, &events).unwrap();

        log::info!("Replayed from snapshot: {:?}", account);
    }

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(1)).await;
    }
}
