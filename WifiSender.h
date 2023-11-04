#include <WiFiEsp.h>
#include <SoftwareSerial.h>

const byte rxPin = 2; 
const byte txPin = 3; 

SoftwareSerial SerialW(rxPin, txPin);

WiFiEspClient client;

const char ssid[] = "yadits";            // your network SSID (name)
const char pass[] = "naomidgi";        // your network password
int status = WL_IDLE_STATUS;     // the Wifi radio's status

const char server[] = "192.168.3.2";
const int port = 3000;

int sessionId = 0;

#define BUFFER_DEPTH_MAX 10
#define BUFFER_DEPTH_TO_SEND 5

float buffer[BUFFER_DEPTH_MAX];
char bufferIdx = 0;

char sendBuffer[70]; // has to be > (6 [size of float '12.34,'] * BUFFER_DEPTH_MAX)
                     // also has to be > 38 + 'int size'*2 (for the seesion Id & time strings)

class WifiSender 
{
public:
  int init()
  {
    SerialW.begin(19200);

    // This part may take 10 seconds...
    WiFi.init(&SerialW);

    if (WiFi.status() == WL_NO_SHIELD) {
      Serial.println("WiFi shield not present");
      return -1;
    }

    return 0;
  }

  void maintain()
  {
    if ( status != WL_CONNECTED) {
      Serial.print("Attempting to connect to WPA SSID: ");
      Serial.println(ssid);
      // Connect to WPA/WPA2 network
      status = WiFi.begin(ssid, pass);

      if ( status == WL_CONNECTED) {
        // you're connected now, so print out the data
        Serial.println("You're connected to the network");
        
        printWifiStatus();
      }

      return; // re-try in the next iteration...
    }

    if ( status == WL_CONNECTED && sessionId == 0) {
      updateSessionId();
    }

    // flush whatever there is in the connection...
    if (client.connected()) {
      while (client.available()) {
        client.read(sendBuffer, sizeof(sendBuffer));
      }      
    } else {
      //Serial.println("Disconnecting from server...");
      //client.stop();      
    }
  }

  void update(float val)
  {
    if(bufferIdx < BUFFER_DEPTH_MAX) {
      buffer[bufferIdx] = val;
      ++bufferIdx;
    } else {
      Serial.println("Error: buffer got full");
    }

    if(bufferIdx > BUFFER_DEPTH_TO_SEND) {
      Serial.println("- Sending " + String((int)bufferIdx) + " measurments to server -");
      if(!client.connected()) {
        Serial.println("Re-Connect to server");
        client.connect(server, port);
      }

      if(client.connected()) {
        Serial.println("Sending update");

        client.println("POST /update HTTP/1.1");
        client.println("Host: "+String(server)+":"+String(port));
        client.println("Content-Type:application/json");
        client.println("Transfer-Encoding: chunked");
        //client.println("Connection: keep-alive"); // keep-alive is infered in HTTP 1.1
        client.println();

        int len = sprintf(sendBuffer, "{\"session\":%d,\"time\":%d,\"temps\":[", sessionId, millis()/1000); // 38 chars without the ints
        client.println(String(len, 16));
        client.println(sendBuffer);

        len = 0;
        for(int i = 0; i < bufferIdx; i++) {
          dtostrf(buffer[i], 1, 2, sendBuffer+len);
          len += strlen(sendBuffer+len);
          sendBuffer[len]=',';
          len++;
        }
        len--;
        len += sprintf(sendBuffer+len, "]}");
        client.println(String(len, 16));
        client.println(sendBuffer);

        client.println("0");
        client.println();

        bufferIdx = 0;

      } else {
        Serial.println("Error: failed to connect to server");
      }
    }
  }

  void updateSessionId()
  {
    Serial.println("- updateSessionId -");
    if (client.connect(server, port)) {
        Serial.println("Connected to server");

        client.println("POST /createSession HTTP/1.1");
        client.println("Host: "+String(server)+":"+String(port));
        client.println("Content-Length: 0");
        //client.println("Connection: keep-alive");  // keep-alive is infered in HTTP 1.1
        client.println();
        
        int lineBreakCount = 0;
        if (client.connected()) {
          while (client.available() && lineBreakCount < 4) {
            char c = client.read();
            Serial.write(c); // DEBUG!
            if(c == '\n' || c == '\r')
              lineBreakCount++;
            else 
              lineBreakCount = 0;            
          }

          int len = 0;
          if(lineBreakCount == 4) {
            while (client.available()) {
              len += client.read(sendBuffer+len, sizeof(sendBuffer)-len);              
              sendBuffer[len] = 0;
              Serial.print(sendBuffer); // DEBUG!!
            }
            sessionId = atoi(sendBuffer);
            Serial.println("session ID is: " + String(sessionId));
          } else {
            Serial.println("server response did contain \\r\\n\\r\\n");
          }
        }        
    } else {
      Serial.println("Error: failed to connect to server");
    }
  }

  void printWifiStatus()
  {
    // print the SSID of the network you're attached to
    Serial.print("SSID: ");
    Serial.println(WiFi.SSID());

    // print your WiFi shield's IP address
    IPAddress ip = WiFi.localIP();
    Serial.print("IP Address: ");
    Serial.println(ip);

    // print the received signal strength
    long rssi = WiFi.RSSI();
    Serial.print("Signal strength (RSSI):");
    Serial.print(rssi);
    Serial.println(" dBm");
  }

};
