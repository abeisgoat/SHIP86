# SHIPx86
![Case Render](case_render.png)

Files for the SHIPx86 console and cartridges.

## About

The SHIPx86 is a small [LattePanda Iota](https://www.dfrobot.com/product-2989.html?tracking=FZm4ZO4beBvpFJyQeYvOfK73VSO81a5YeZVG6Dvdt6PuUlu5E3Kr5BJSV9GsJZ59) powered computer which uses retro style cartridges to store movies, games, and whatever else. These messy files are shared with no warranty for those who wish to try to recreate the device!

This repo contains...

* `automon` - The code to automatically monitor and run carts. Pull this repo down and run `./install.sh` on the Iota and it should install it into the background.
* `cart_reader` - The files required to manufacture the USB SD card reader PCB. Note that the 40-pin edge connector will need to be bought and soldered seperately. (see parts list).
* `carts` - The files required to manufacture a cart PCB and an STL for the plastic cover. These should be made of **1mm thick PCBs** to ensure a soft but stable fit.
* `case` - The STLs for the device case.
* `case_pcb` - The files required to manufacture the internal PCBs used in the case.

## Parts

Various small parts are required to build this thing! Here's a bunch of affiliate links to those parts...

* [LattePanda Iota](https://www.dfrobot.com/product-2989.html?tracking=FZm4ZO4beBvpFJyQeYvOfK73VSO81a5YeZVG6Dvdt6PuUlu5E3Kr5BJSV9GsJZ59)
* [LattePanda Iota PoE Board (only needed for power whip)](https://www.dfrobot.com/product-2984.html?tracking=FZm4ZO4beBvpFJyQeYvOfK73VSO81a5YeZVG6Dvdt6PuUlu5E3Kr5BJSV9GsJZ59)
* [USB PD Controller](https://www.adafruit.com/product/5991)
* [RGB LED Matrix](https://www.adafruit.com/product/5201)
* [Low Profile Switch Sample Pack](https://amzn.to/4aqBNOm)
* [Low Profile Keycap](https://chosfox.com/products/chocfox-cfx-choc-keycaps)
* [BE200 Wifi Card](https://amzn.to/4pKZwxg)
* [Wifi Antenna](https://amzn.to/3Y4toZu)
* [Power Board Connector](https://amzn.to/4s7PZ5c)
* [M2.5 Screw Set](https://amzn.to/4aUPRQg)
* [Heat Shrink Tube](https://amzn.to/4qmboG1)
* [JSH SH Male Connector](https://amzn.to/4pOuO6E)
* [Rubber feet](https://amzn.to/3KUEWLY)
* [40-Pin Edge Connector](https://www.digikey.com/en/products/detail/te-connectivity-amp-connectors/5-5530843-4/770549?s=N4IgTCBcDaIIIGYCMB2MCC0A5AIgAhAF0BfIA)

Optionally, here are the filaments I used in my build.

* [Grey Metal PLA Filament](https://us.store.bambulab.com/products/pla-metal?id=41150855610504)
* [Blue Matte PLA Filament](https://us.store.bambulab.com/products/pla-matte?id=40489682141320)
* [Translucent PETG Filament](https://us.store.bambulab.com/products/petg-translucent?id=42479468281992)

## Tips

### Where should I order PCBs from?
[NextPCB.com](https://www.nextpcb.com/) has sponsored my videos for years and I've always found their work to be high quality. The included BOMs for the cartridge and reader are formatted for their service, however any fabrication house should be capable of producing these simple boards. For the boards used internally in the case, since they do not require PCB assembly I've placed an order with OSHPark to see if that is a good manufacturer - I will update here once I verify them as a good option.

### Why is my case wobbly?
When you screw a bunch of 3D printed parts together, it's easy to over-tighten screws which causes warping. If you find your baseplate doesn't sit flat, loosen all the base screws half a turn, wait 10 minutes, and see if it relaxes to be flat.
