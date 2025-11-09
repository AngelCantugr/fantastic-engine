package protocol

import (
	"bufio"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
	"net"
	"sync"
)

// MessageType represents different message types
type MessageType byte

const (
	MsgPing MessageType = iota
	MsgPong
	MsgData
	MsgAck
	MsgError
)

// Message represents a protocol message
type Message struct {
	Type    MessageType
	Payload []byte
}

// Protocol constants
const (
	MaxPayloadSize = 1024 * 1024 // 1MB
	HeaderSize     = 5            // 1 byte type + 4 bytes length
)

// Encode encodes a message to binary format
// Format: [Type:1byte][Length:4bytes][Payload:Nbytes]
func (m *Message) Encode() ([]byte, error) {
	if len(m.Payload) > MaxPayloadSize {
		return nil, errors.New("payload too large")
	}

	buf := make([]byte, HeaderSize+len(m.Payload))
	buf[0] = byte(m.Type)
	binary.BigEndian.PutUint32(buf[1:5], uint32(len(m.Payload)))
	copy(buf[5:], m.Payload)

	return buf, nil
}

// DecodeMessage decodes a message from a reader
func DecodeMessage(r io.Reader) (*Message, error) {
	header := make([]byte, HeaderSize)
	if _, err := io.ReadFull(r, header); err != nil {
		return nil, err
	}

	msgType := MessageType(header[0])
	length := binary.BigEndian.Uint32(header[1:5])

	if length > MaxPayloadSize {
		return nil, errors.New("payload too large")
	}

	payload := make([]byte, length)
	if length > 0 {
		if _, err := io.ReadFull(r, payload); err != nil {
			return nil, err
		}
	}

	return &Message{
		Type:    msgType,
		Payload: payload,
	}, nil
}

// ConnectionState represents protocol state
type ConnectionState int

const (
	StateNew ConnectionState = iota
	StateConnected
	StateAuthenticated
	StateClosed
)

// Connection manages a protocol connection
type Connection struct {
	conn   net.Conn
	state  ConnectionState
	reader *bufio.Reader
	writer *bufio.Writer
	mu     sync.Mutex
}

func NewConnection(conn net.Conn) *Connection {
	return &Connection{
		conn:   conn,
		state:  StateNew,
		reader: bufio.NewReader(conn),
		writer: bufio.NewWriter(conn),
	}
}

func (c *Connection) SendMessage(msg *Message) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if c.state == StateClosed {
		return errors.New("connection closed")
	}

	data, err := msg.Encode()
	if err != nil {
		return err
	}

	if _, err := c.writer.Write(data); err != nil {
		return err
	}

	return c.writer.Flush()
}

func (c *Connection) ReceiveMessage() (*Message, error) {
	return DecodeMessage(c.reader)
}

func (c *Connection) Close() error {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.state = StateClosed
	return c.conn.Close()
}

func (c *Connection) State() ConnectionState {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.state
}

func (c *Connection) SetState(state ConnectionState) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.state = state
}

// Server implements the protocol server
type Server struct {
	addr     string
	listener net.Listener
	handler  func(*Connection)
	mu       sync.Mutex
	conns    map[*Connection]bool
}

func NewServer(addr string, handler func(*Connection)) *Server {
	return &Server{
		addr:    addr,
		handler: handler,
		conns:   make(map[*Connection]bool),
	}
}

func (s *Server) Start() error {
	listener, err := net.Listen("tcp", s.addr)
	if err != nil {
		return err
	}

	s.listener = listener

	go s.accept()
	return nil
}

func (s *Server) accept() {
	for {
		conn, err := s.listener.Accept()
		if err != nil {
			return
		}

		c := NewConnection(conn)
		c.SetState(StateConnected)

		s.mu.Lock()
		s.conns[c] = true
		s.mu.Unlock()

		go func() {
			s.handler(c)

			s.mu.Lock()
			delete(s.conns, c)
			s.mu.Unlock()

			c.Close()
		}()
	}
}

func (s *Server) Stop() error {
	if s.listener != nil {
		return s.listener.Close()
	}
	return nil
}

// Client implements the protocol client
type Client struct {
	conn *Connection
}

func NewClient(addr string) (*Client, error) {
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		return nil, err
	}

	c := NewConnection(conn)
	c.SetState(StateConnected)

	return &Client{conn: c}, nil
}

func (c *Client) Send(msg *Message) error {
	return c.conn.SendMessage(msg)
}

func (c *Client) Receive() (*Message, error) {
	return c.conn.ReceiveMessage()
}

func (c *Client) Close() error {
	return c.conn.Close()
}

// Ping sends a ping and waits for pong
func (c *Client) Ping() error {
	if err := c.Send(&Message{Type: MsgPing}); err != nil {
		return err
	}

	msg, err := c.Receive()
	if err != nil {
		return err
	}

	if msg.Type != MsgPong {
		return fmt.Errorf("expected pong, got %v", msg.Type)
	}

	return nil
}

// SendData sends data and waits for acknowledgment
func (c *Client) SendData(data []byte) error {
	if err := c.Send(&Message{Type: MsgData, Payload: data}); err != nil {
		return err
	}

	msg, err := c.Receive()
	if err != nil {
		return err
	}

	if msg.Type != MsgAck {
		return fmt.Errorf("expected ack, got %v", msg.Type)
	}

	return nil
}
