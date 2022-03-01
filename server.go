package main

import (
	"fmt"
	"log"
	"net"
	"os"
	"strconv"
	"time"
)

func main() {

	usage()

	maxTimeGap, err := time.ParseDuration("10m")
	if err != nil {
		log.Fatal("Couldn't parse desired time gap duration: %v\n", err)
	}

	ip := os.Args[1]
	port, _ := strconv.Atoi(os.Args[2])

	addr := net.UDPAddr{Port: port, IP: net.ParseIP(ip)}

	conn, err := net.ListenUDP("udp", &addr)
	if err != nil {
		log.Fatal(err)
	}

	b := make([]byte, 2048)

	lastPacketRecvd := time.Now()

	for i := 0; true; i++ {
		cc, _, rderr := conn.ReadFromUDP(b)
		currently := time.Now()

		if rderr != nil {
			fmt.Printf("net.ReadFromUDP() error: %s\n", rderr)
		} else {
			if i > 0 {
				if gap := currently.Sub(lastPacketRecvd); gap > maxTimeGap {
					fmt.Printf("# Gap in receptions: %v\n\n", gap)
				}
			}
			fmt.Printf("%s\t%s\n", time.Now().Format(time.RFC3339), string(b[:cc]))

			lastPacketRecvd = currently
		}
	}
}

func usage() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "%s - UDP echo server\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Usage: %s <IP> <portno>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "you have to specify an IP address, even if it's only 127.0.0.1\n")
		os.Exit(1)
	}
}
