# Sprint 4 Network Report

## Topology

This network has two clients, one server, and one router.

- ET-Client1 uses `192.168.10.0/24`
- ET-Client2 uses `192.168.11.0/24`
- ET-Server uses `192.168.20.100`
- ET-R1 connects all three networks

![Topology](sprint_4_topology.png)

## Router and DHCP

ET-R1 addresses:

- `192.168.10.1` for Client 1
- `192.168.11.1` for Client 2
- `192.168.20.1` for the server

Client 1 received `192.168.10.2` through DHCP. Client 2 received `192.168.11.2` through DHCP.

![Router status](sprint_4_router_status.png)

![DHCP bindings](sprint_4_dhcp_bindings.png)

## Tests

Both clients successfully pinged the server at `192.168.20.100` with 0% packet loss.

Both clients also used the router as their DNS server. The name `server.tomlinson.edu` resolved to `192.168.20.100`.

## DNS Capture

The packet capture shows Client 1 asking the router for the address of `server.tomlinson.edu`.

The router replied with `192.168.20.100`, which is the server’s address.

![DNS capture](sprint_4_dns_capture.png)

