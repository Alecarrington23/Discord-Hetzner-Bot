from hcloud import Client
from hcloud.images.domain import Image
from hcloud.servers.domain import Server
from hcloud.server_types.domain import ServerType
from hcloud.volumes.domain import Volume
from hcloud.locations.domain import Location
import asyncio

class GameData:
    running = False

    def __init__(self, token, name, servertype, snapshot, location, volume):
        self.name = name
        self.servertype = servertype.strip() if isinstance(servertype, str) else servertype
        self.client = Client(token=token)

        # --- snapshot/image (optional) ---
        # If snapshot is None => we'll fall back to Ubuntu 24.04 in start()
        self.snapshot = None
        if snapshot is not None:
            images = self.client.images.get_all()
            for img in images:
                # support matching by description OR name
                if img.data_model.description == snapshot or img.data_model.name == snapshot:
                    self.snapshot = img.data_model.id
                    break
            if self.snapshot is None:
                raise ValueError(f"Snapshot/Image not found: {snapshot}")

        # --- location (required) ---
        self.location = None
        locations = self.client.locations.get_all()
        for loc in locations:
            if loc.data_model.name == location:
                self.location = loc.data_model.id
                break
        if self.location is None:
            raise ValueError(f"Location not found: {location}")

        # --- volume (optional) ---
        self.volume = None
        if volume is not None:
            volumes = self.client.volumes.get_all()
            for vol in volumes:
                if vol.data_model.name == volume and vol.data_model.location.data_model.id == self.location:
                    self.volume = vol.data_model.id
                    break
            if self.volume is None:
                raise ValueError(f"Volume not found in location {location}: {volume}")

        # --- check for existing server by name ---
        servers = self.client.servers.get_all()
        self.server = None
        for s in servers:
            if s.data_model.name == name:
                self.server = s  # keep the Server object
                self.running = True
                print("existing server " + self.server.status)

    async def start(self):
        if not self.running:
            print("Starting " + self.name)

            # Choose image:
            # - if snapshot provided => use that snapshot image id
            # - else => boot from Ubuntu 24.04 (Hetzner public image name)
            image = Image(self.snapshot) if self.snapshot is not None else "ubuntu-24.04"

            # Attach volume only if configured
            volumes = [Volume(self.volume)] if self.volume is not None else None

            response = self.client.servers.create(
                name=self.name,
                server_type=ServerType(name=self.servertype),
                image=image,
                location=Location(self.location),
                volumes=volumes
            )
            self.server = response.server
            self.running = True
        else:
            print(self.name + " is already running")

    async def stop(self):
        if self.running:
            print("Stopping " + self.name)

            self.client.servers.shutdown(self.server)

            # Give it time to begin shutdown, then poll status
            await asyncio.sleep(5)

            while True:
                serv = self.client.servers.get_by_id(self.server.id)
                self.server = serv
                print(self.server.status)
                if self.server.status == Server.STATUS_OFF:
                    break
                await asyncio.sleep(5)

            print("Server is now stopped")

            # Detach volume only if configured
            if self.volume is not None:
                self.client.volumes.detach(Volume(self.volume))
                await asyncio.sleep(1)

            self.client.servers.delete(self.server)
            self.running = False
            self.server = None
        else:
            print(self.name + " isn't running")

    def status(self):
        msg = self.name
        if self.server is None:
            msg += " isn't running"
        else:
            self.server = self.client.servers.get_by_id(self.server.id)
            msg += " is in status "
            msg += self.server.status
            msg += "\n"
            msg += "and has the IP:\n"
            ip = self.server.public_net.ipv4.ip
            msg += ip + "\n"
        return msg

    def isRunning(self):
        return self.running