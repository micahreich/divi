# Divi: mobile speaker platform

## Running SnapServer + SnapClient

On each Orin, run the following commands
```bash
snapclient -h mreich-asuslaptop-q540vj --soundcard right_only # right speaker
snapclient -h mreich-asuslaptop-q540vj --soundcard left_only # left speaker
```

From the master laptop, ensure SnapServer is running, then run the following command:
```bash
ffmpeg -f pulse -i alsa_output.pci-0000_00_1f.3-platform-skl_hda_dsp_generic.HiFi__hw_sofhdadsp__sink.monitor -f s16le -ar 48000 -ac 2 /tmp/snapfifo
```

On the master laptop, run firefox with:
```bash
ALSA_PLUGIN_DIR=/usr/lib/x86_64-linux-gnu/alsa-lib firefox
```