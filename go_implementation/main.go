package main

import (
	"encoding/json"
	"fmt"
	"log"

	"golang.org/x/net/websocket"
)

var SYMBOLS = []string{
	"PI_XBTUSD",
	"PI_ETHUSD",
	"PI_XRPUSD",
	"FI_ETHUSD_210625",
	"FI_XBTUSD_210625",
}

const URL = "wss://futures.kraken.com/ws/v1"

func main() {
	client, err := NewKrakenClient(URL)
	if err != nil {
		log.Fatal(err)
	}
	if err := client.Subscribe(SYMBOLS); err != nil {
		log.Fatal(err)
	}
	client.Consume()
}

type KrakenClient struct {
	Url string
	ws  *websocket.Conn
}

func NewKrakenClient(url string) (*KrakenClient, error) {
	ws, err := websocket.Dial(url, "", "http://localhost/")
	if err != nil {
		return nil, err
	}
	return &KrakenClient{
		Url: url,
		ws:  ws,
	}, nil
}

func (c *KrakenClient) Subscribe(symbols []string) error {
	subscribe, err := CreateSymbolSubscribe(symbols)
	if err != nil {
		return err
	}
	heartbeat, err := CreateHeartbeatSubscribe()
	if err != nil {
		return err
	}

	if _, err := c.ws.Write(subscribe); err != nil {
		return err
	}
	if _, err := c.ws.Write(heartbeat); err != nil {
		return err
	}
	return nil
}

func (c *KrakenClient) Consume() {
	for {
		var msg = make([]byte, 512)
		n, err := c.ws.Read(msg)
		if err != nil {
			log.Fatal(err)
		}
		fmt.Printf("Received: %s.\n", msg[:n])
	}
}

type BaseSubscribeEvent struct {
	Event string `json:"event"`
	Feed  string `json:"feed"`
}

func CreateHeartbeatSubscribe() ([]byte, error) {
	e, err := json.Marshal(BaseSubscribeEvent{
		Event: "subscribe",
		Feed:  "ticker",
	})
	if err != nil {
		return nil, err
	}
	return e, nil
}

type SymbolSubscribeEvent struct {
	BaseSubscribeEvent
	ProductIds []string `json:"product_ids"`
}

func CreateSymbolSubscribe(symbols []string) ([]byte, error) {
	e, err := json.Marshal(SymbolSubscribeEvent{
		BaseSubscribeEvent: BaseSubscribeEvent{
			Event: "subscribe",
			Feed:  "ticker",
		},
		ProductIds: symbols,
	})
	if err != nil {
		return nil, err
	}
	return e, nil
}
