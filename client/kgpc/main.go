package main

import (
	"context"
	"fmt"
	"net"
	"os"
	"regexp"

	"nhooyr.io/websocket"
)

func main() {
	var (
		cli  Client
		err  error
		dest string
	)

	if len(os.Args) <= 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s [server address] [command ...]\n",
			os.Args[0])
		os.Exit(1)
	}

	dest = os.Args[1]
	if ok, _ := regexp.MatchString(`^wss?://`, dest); ok {
		ctx := context.Background()
		c, _, err := websocket.Dial(ctx, dest, nil)
		if err == nil {
			cli.Rwc = websocket.NetConn(ctx, c, websocket.MessageText)
		}
	} else {
		if ok, _ := regexp.MatchString(`^:\d+$`, dest); !ok {
			dest += ":2671"
		}
		cli.Rwc, err = net.Dial("tcp", dest)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

	cli.Handle()
}
