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

	fileName := os.Args[1]
	ip := os.Args[2]
	port, _ := strconv.Atoi(os.Args[3])

	fout, err := os.OpenFile(fileName, os.O_WRONLY|os.O_APPEND|os.O_CREATE, 0666)
	if err != nil {
		log.Fatal(err)
	}

	addr := net.UDPAddr{Port: port, IP: net.ParseIP(ip)}

	conn, err := net.ListenUDP("udp", &addr)
	if err != nil {
		log.Fatal(err)
	}

	b := make([]byte, 2048)

	lastPacketRecvd := time.Now()
	fmt.Fprintf(fout, "\n# Server starting %s\n", lastPacketRecvd.Format(time.RFC3339))

	for i := 0; true; i++ {
		cc, _, err := conn.ReadFromUDP(b)
		currently := time.Now()

		if err != nil {
			fmt.Fprintf(fout, "# %s net.ReadFromUDP() error: %s\n", time.Now().Format(time.RFC3339), err)
		} else {
			if i > 0 {
				if gap := currently.Sub(lastPacketRecvd); gap > maxTimeGap {
					fmt.Printf("# Gap in receptions: %v\n\n", gap)
				}
			}
			fmt.Fprintf(fout, "%s\t%s\n", time.Now().Format(time.RFC3339), string(b[:cc]))

			lastPacketRecvd = currently
		}
	}
}

func usage() {
	if len(os.Args) < 4 {
		fmt.Fprintf(os.Stderr, "%s - UDP echo server\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "Usage: %s <logfile> <IP> <portno>\n", os.Args[0])
		fmt.Fprintf(os.Stderr, "you have to specify an IP address, even if it's only 127.0.0.1\n")
		os.Exit(1)
	}
}
