# seomaps

seomaps is a Python wrapper around Folium for those who just want a quick and dirty way of seeing simple data on a map, with steps required to set it up particularly for an offline node running Windows.

## Prerequisites

Styles, sprites, icons default to [osm-liberty](https://github.com/maputnik/osm-liberty). Clone the repository to retrieve the sprites (really the only folder that we'll need).
Using osm-liberty cause it's prettier.

Install Docker. We'll be using [Tileserver GL](https://tileserver.readthedocs.io/en/latest/installation.html) via Docker.

## Usage

Detailed commands may be found in the text files, but the general command on Windows will look something like

```bash
docker run --rm -it -v /f/tilestest:/data -p 8080:80 maptiler/tileserver-gl --mbtiles osm-2017-07-03-v3_6_1-planet.mbtiles --verbose -c osm_liberty_config.json
```

where the directory used here to store the tiles is

```bash
F:\tilestest
```

and so the docker argument "-v /f/tilestest:/data" should be changed to "-v whatever/your/path/is:/data".


## Offline Usage

First get the image on the online computer (with Docker on it).

```bash
docker pull maptiler/tileserver-gl
```

On the online computer, save the image to a single tar file by running

```bash
docker image save --output tileserver-gl.tar maptiler/tileserver-gl
```

and then copy the file over to the offline computer.
On the offline computer (also with Docker running), run the command:

```bash
docker image load -i tileserver-gl.tar
```

You should now be able to run the command from the previous section

```bash
docker run ....
```

and it should find the existing image.

## Notes on Directory Usage and Docker Installation

Docker installation on Windows is, as of 11th Dec 2020, unable to set install directories and use directories.
Found some pages online which recommend setting some environment variables and running in administrator to move the Docker installation,
but it doesn't seem to affect the eventual virtual hard drives (refer to dockerCustomInstall.bat).

In particular, on Windows it appears that the images get stored directly into C:\Users\CurrentUser\AppData\Local\Docker\wsl.
The 2 vhdx files appear to keep growing even if you remove and reinstall the same image, unsure how to manage this.
