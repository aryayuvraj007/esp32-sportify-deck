
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define OLED_ADDR 0x3C

Adafruit_SSD1306 display(
  SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET
);

String song = "Waiting...";
String artist = "Spotify Deck";
String album = "";

int durationSec = 240;
int progressSec = 0;
bool isPlaying = false;

void drawScreen() {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);

  // Header
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.print("SPOTIFY DECK");

  display.drawLine(0, 11, 127, 11, SSD1306_WHITE);

  // Song title
  display.setTextSize(1);
  display.setCursor(0, 17);

  if (song.length() > 21)
    display.print(song.substring(0, 21));
  else
    display.print(song);

  // Artist
  display.setCursor(0, 29);
  if (artist.length() > 21)
    display.print(artist.substring(0, 21));
  else
    display.print(artist);

  // Playback status
  display.setCursor(0, 43);
  display.print(isPlaying ? "PLAYING" : "PAUSED");

  // Progress bar
  int barWidth = 126;
  int filled = 0;

  if (durationSec > 0) {
    filled = (progressSec * barWidth) / durationSec;
    filled = constrain(filled, 0, barWidth);
  }

  display.drawRect(0, 55, 128, 5, SSD1306_WHITE);

  if (filled > 0)
    display.fillRect(1, 56, min(filled, 126), 3, SSD1306_WHITE);

  display.display();
}

void processCommand(String line) {
  line.trim();

  // Track information
  if (line.startsWith("T:")) {

    String data = line.substring(2);

    int i0 = data.indexOf('\t');
    int i1 = data.indexOf('\t', i0 + 1);
    int i2 = data.indexOf('\t', i1 + 1);
    int i3 = data.indexOf('\t', i2 + 1);
    int i4 = data.indexOf('\t', i3 + 1);
    int i5 = data.indexOf('\t', i4 + 1);

    if (i0 < 0 || i1 < 0 || i2 < 0) return;

    song = data.substring(0, i0);
    artist = data.substring(i0 + 1, i1);
    album = data.substring(i1 + 1, i2);

    if (i3 >= 0)
      durationSec = data.substring(i2 + 1, i3).toInt();

    if (i4 >= 0)
      progressSec = data.substring(i3 + 1, i4).toInt();

    if (i5 >= 0)
      isPlaying = data.substring(i4 + 1, i5) == "1";

    drawScreen();
  }

  // Progress update
  else if (line.startsWith("P:")) {

    String data = line.substring(2);
    int tab = data.indexOf('\t');

    if (tab >= 0) {
      progressSec = data.substring(0, tab).toInt();
      isPlaying = data.substring(tab + 1) == "1";
      drawScreen();
    }
  }

  // Album art: consume binary bytes because OLED cannot display it
  else if (line.startsWith("A:")) {

    String data = line.substring(2);

    int comma1 = data.indexOf(',');
    int comma2 = data.indexOf(',', comma1 + 1);

    if (comma1 >= 0 && comma2 >= 0) {
      int bytes = data.substring(comma2 + 1).toInt();

      while (bytes > 0) {
        if (Serial.available()) {
          Serial.read();
          bytes--;
        }
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  Wire.begin(21, 22);

  if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR)) {
    while (true);
  }

  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(1);
  display.setCursor(15, 20);
  display.println("SPOTIFY DECK");
  display.setCursor(20, 35);
  display.println("Connecting...");
  display.display();

  Serial.println("SPOTIFY_DECK_READY");
}

void loop() {
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    processCommand(line);
  }
}
