package protocol

import (
	"bytes"
	"testing"
	"time"
)

func TestMessageEncodeDecode(t *testing.T) {
	msg := &Message{
		Type:    MsgData,
		Payload: []byte("Hello, Protocol!"),
	}

	encoded, err := msg.Encode()
	if err != nil {
		t.Fatalf("Failed to encode: %v", err)
	}

	decoded, err := DecodeMessage(bytes.NewReader(encoded))
	if err != nil {
		t.Fatalf("Failed to decode: %v", err)
	}

	if decoded.Type != msg.Type {
		t.Errorf("Type mismatch: expected %v, got %v", msg.Type, decoded.Type)
	}

	if !bytes.Equal(decoded.Payload, msg.Payload) {
		t.Errorf("Payload mismatch")
	}
}

func TestClientServer(t *testing.T) {
	// Start server
	server := NewServer(":0", func(conn *Connection) {
		for {
			msg, err := conn.ReceiveMessage()
			if err != nil {
				return
			}

			switch msg.Type {
			case MsgPing:
				conn.SendMessage(&Message{Type: MsgPong})
			case MsgData:
				conn.SendMessage(&Message{Type: MsgAck})
			}
		}
	})

	if err := server.Start(); err != nil {
		t.Fatalf("Failed to start server: %v", err)
	}
	defer server.Stop()

	// Get actual address
	addr := server.listener.Addr().String()

	time.Sleep(100 * time.Millisecond)

	// Connect client
	client, err := NewClient(addr)
	if err != nil {
		t.Fatalf("Failed to connect: %v", err)
	}
	defer client.Close()

	// Test ping
	if err := client.Ping(); err != nil {
		t.Errorf("Ping failed: %v", err)
	}

	// Test data send
	if err := client.SendData([]byte("test data")); err != nil {
		t.Errorf("SendData failed: %v", err)
	}
}

func TestConnectionState(t *testing.T) {
	server := NewServer(":0", func(conn *Connection) {
		if conn.State() != StateConnected {
			t.Error("Expected connection to be in Connected state")
		}
	})

	server.Start()
	defer server.Stop()

	addr := server.listener.Addr().String()
	time.Sleep(100 * time.Millisecond)

	client, _ := NewClient(addr)
	defer client.Close()

	time.Sleep(100 * time.Millisecond)
}

func BenchmarkMessageEncode(b *testing.B) {
	msg := &Message{
		Type:    MsgData,
		Payload: make([]byte, 1024),
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		msg.Encode()
	}
}

func BenchmarkMessageDecode(b *testing.B) {
	msg := &Message{
		Type:    MsgData,
		Payload: make([]byte, 1024),
	}

	encoded, _ := msg.Encode()
	b.ResetTimer()

	for i := 0; i < b.N; i++ {
		DecodeMessage(bytes.NewReader(encoded))
	}
}
