#!/usr/bin/env python3
import socket
import threading
import random
import string
import time
import argparse
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('tcp-fuzzer')

# Default settings
DEFAULT_HOST = '127.0.0.1'
DEFAULT_PORT = 8888
DEFAULT_BUFFER_SIZE = 1024


class SimpleProtocolServer:
    """A simple TCP server that implements a basic protocol."""
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self.clients = []
        
    def start(self):
        """Start the TCP server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.sock.listen(5)
            self.running = True
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client, address = self.sock.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.clients.append((client, client_thread))
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                        
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, address):
        """Handle a client connection."""
        logger.info(f"New connection from {address[0]}:{address[1]}")
        
        try:
            while self.running:
                # Simple protocol:
                # HELLO -> respond with HELLO\n
                # ECHO <message> -> respond with <message>\n
                # INFO -> respond with SERVER_INFO:SimpleProtocol:1.0\n
                # BYE -> close connection
                data = client_socket.recv(DEFAULT_BUFFER_SIZE)
                if not data:
                    break
                
                try:
                    decoded_data = data.decode('utf-8').strip()
                    logger.info(f"Received from {address}: {decoded_data}")
                    
                    if decoded_data == "HELLO":
                        response = "HELLO\n"
                    elif decoded_data.startswith("ECHO "):
                        message = decoded_data[5:]  # Extract message after "ECHO "
                        response = f"{message}\n"
                    elif decoded_data == "INFO":
                        response = "SERVER_INFO:SimpleProtocol:1.0\n"
                    elif decoded_data == "BYE":
                        response = "GOODBYE\n"
                        client_socket.send(response.encode('utf-8'))
                        break
                    else:
                        response = "ERROR:Unknown command\n"
                    
                    client_socket.send(response.encode('utf-8'))
                    
                except UnicodeDecodeError:
                    # Handle binary or malformed data
                    logger.warning(f"Received non-UTF8 data from {address}")
                    client_socket.send(b"ERROR:Invalid encoding\n")
                
        except ConnectionResetError:
            logger.info(f"Connection reset by {address[0]}:{address[1]}")
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Connection closed with {address[0]}:{address[1]}")
    
    def stop(self):
        """Stop the server and close all connections."""
        logger.info("Stopping server...")
        self.running = False
        
        # Close all client connections
        for client, _ in self.clients:
            try:
                client.close()
            except:
                pass
        
        # Close server socket
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        
        logger.info("Server stopped")


class ProtocolFuzzer:
    """A TCP protocol fuzzer that generates and sends malformed data."""
    
    def __init__(self, target_host=DEFAULT_HOST, target_port=DEFAULT_PORT):
        self.target_host = target_host
        self.target_port = target_port
        self.running = False
        self.valid_commands = ["HELLO", "ECHO", "INFO", "BYE"]
        self.sock = None
        
    def connect(self):
        """Connect to the target server."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.target_host, self.target_port))
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the target server."""
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None
    
    def send_and_receive(self, data, binary=False):
        """Send data to the server and receive response."""
        try:
            if not self.sock and not self.connect():
                return None
            
            if binary:
                self.sock.send(data)
            else:
                self.sock.send(data.encode('utf-8'))
            
            response = self.sock.recv(DEFAULT_BUFFER_SIZE)
            return response
        except socket.timeout:
            logger.warning("Socket timeout - no response received")
            return None
        except Exception as e:
            logger.error(f"Error in send_and_receive: {e}")
            self.disconnect()
            return None
    
    def generate_fuzzing_payloads(self):
        """Generate various fuzzing payloads."""
        payloads = []
        
        # Basic command fuzzing
        for cmd in self.valid_commands:
            # Valid command as baseline
            payloads.append(cmd)
            
            # Command case variations
            payloads.append(cmd.lower())
            payloads.append(cmd.upper())
            
            # Command with whitespace
            payloads.append(f" {cmd}")
            payloads.append(f"{cmd} ")
            payloads.append(f"  {cmd}  ")
            
            # Command repetition
            payloads.append(f"{cmd}{cmd}")
            payloads.append(f"{cmd} {cmd}")
        
        # Long string payloads (potential buffer overflows)
        payloads.append("A" * 100)
        payloads.append("A" * 1000)
        payloads.append("A" * 5000)
        
        # ECHO command with various payloads
        payloads.append("ECHO " + "A" * 100)
        payloads.append("ECHO " + "A" * 1000)
        payloads.append("ECHO " + "%" * 1000)  # Format string test
        
        # Special characters
        special_chars = "%s%x%n\\\"';DROP TABLE users;--"
        payloads.append(special_chars)
        payloads.append("ECHO " + special_chars)
        
        # SQL injection patterns
        payloads.append("ECHO ' OR '1'='1")
        
        # Command injection patterns
        payloads.append("ECHO `ls -la`")
        payloads.append("ECHO $(ls -la)")
        
        # Format string vulnerabilities
        payloads.append("ECHO %x%x%x%x")
        payloads.append("ECHO %n%n%n%n")
        
        # Non-ASCII characters
        payloads.append("ECHO ÿÿÿÿÿÿ")
        
        # Null bytes and control characters
        payloads.append("ECHO \x00\x01\x02\x03\x04")
        
        # Random binary data
        random_binary = bytes([random.randint(0, 255) for _ in range(100)])
        
        return payloads, random_binary
    
    def start_fuzzing(self, delay=0.5, rounds=1):
        """Start the fuzzing process."""
        logger.info(f"Starting fuzzer against {self.target_host}:{self.target_port}")
        self.running = True
        
        try:
            for round_num in range(1, rounds + 1):
                logger.info(f"Fuzzing round {round_num}/{rounds}")
                
                payloads, random_binary = self.generate_fuzzing_payloads()
                
                # Test standard payloads
                for i, payload in enumerate(payloads):
                    if not self.running:
                        break
                    
                    logger.info(f"Sending payload {i+1}/{len(payloads)}: {payload[:30]}{'...' if len(payload) > 30 else ''}")
                    response = self.send_and_receive(payload)
                    
                    if response:
                        try:
                            decoded = response.decode('utf-8').strip()
                            logger.info(f"Response: {decoded[:100]}")
                        except UnicodeDecodeError:
                            logger.info(f"Binary response: {response[:20]}")
                    else:
                        logger.warning("No response or connection lost")
                        self.connect()  # Try to reconnect
                    
                    time.sleep(delay)
                
                # Test binary payload
                if self.running:
                    logger.info("Sending random binary payload")
                    response = self.send_and_receive(random_binary, binary=True)
                    
                    if response:
                        logger.info(f"Binary response received: {len(response)} bytes")
                    else:
                        logger.warning("No response to binary payload or connection lost")
                        self.connect()
                
                logger.info(f"Completed fuzzing round {round_num}")
                
            logger.info("Fuzzing completed")
            
        except KeyboardInterrupt:
            logger.info("Fuzzing interrupted")
        finally:
            self.running = False
            self.disconnect()
    
    def stop_fuzzing(self):
        """Stop the fuzzing process."""
        self.running = False
        self.disconnect()


def run_server(host, port):
    """Run the TCP server."""
    server = SimpleProtocolServer(host, port)
    server_thread = threading.Thread(target=server.start)
    server_thread.daemon = True
    server_thread.start()
    return server, server_thread


def run_fuzzer(host, port, delay, rounds):
    """Run the protocol fuzzer."""
    fuzzer = ProtocolFuzzer(host, port)
    fuzzer_thread = threading.Thread(target=fuzzer.start_fuzzing, args=(delay, rounds))
    fuzzer_thread.daemon = True
    fuzzer_thread.start()
    return fuzzer, fuzzer_thread


def main():
    parser = argparse.ArgumentParser(description='TCP Server and Protocol Fuzzer')
    parser.add_argument('--host', default=DEFAULT_HOST, help=f'Host address (default: {DEFAULT_HOST})')
    parser.add_argument('--port', type=int, default=DEFAULT_PORT, help=f'Port number (default: {DEFAULT_PORT})')
    parser.add_argument('--mode', choices=['server', 'fuzzer', 'both'], default='both', 
                        help='Mode to run: server, fuzzer, or both (default: both)')
    parser.add_argument('--delay', type=float, default=0.5, 
                        help='Delay between fuzzing attempts in seconds (default: 0.5)')
    parser.add_argument('--rounds', type=int, default=1,
                        help='Number of fuzzing rounds (default: 1)')
    
    args = parser.parse_args()
    
    try:
        server = None
        fuzzer = None
        
        if args.mode in ['server', 'both']:
            logger.info(f"Starting server on {args.host}:{args.port}")
            server, server_thread = run_server(args.host, args.port)
            # Give the server time to start before fuzzing
            if args.mode == 'both':
                time.sleep(1)
        
        if args.mode in ['fuzzer', 'both']:
            logger.info(f"Starting fuzzer targeting {args.host}:{args.port}")
            fuzzer, fuzzer_thread = run_fuzzer(args.host, args.port, args.delay, args.rounds)
        
        # Keep the main thread running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if fuzzer:
                fuzzer.stop_fuzzing()
            if server:
                server.stop()
    
    except Exception as e:
        logger.error(f"Error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()