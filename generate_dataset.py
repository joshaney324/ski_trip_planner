import json
import csv
import random

TARGET = 80

random.seed(42)


EARTH_PREFIXES = [
    "Mount", "Mt.", "Big", "Little", "Grand", "Great", "Wild", "Frozen",
    "Slippery", "Icy", "Soggy", "Crusty", "Fluffy", "Gnarly", "Sketchy",
    "Spicy", "Mediocre", "Peak", "Sir", "Lord", "Baron", "Count",
    "Professor", "Doctor", "Captain", "Colonel", "General", "Admiral",
    "Ancient", "Haunted", "Cursed", "Blessed", "Enchanted", "Forgotten",
    "Overcrowded", "Underrated", "Overrated", "Discount", "Luxury",
    "Budget", "Premium", "Ultra", "Mega", "Hyper", "Super", "Turbo",
]

EARTH_NAMES = [
    "Yodeler", "Mogul", "Powder Keg", "Face Plant", "Wipeout", "Yard Sale",
    "Apres Ski", "Hot Toddy", "Ski Bum", "Chairlift", "Gondola", "Groomer",
    "Black Diamond", "Blue Square", "Green Circle", "Double Black",
    "Bunny Slope", "Cat Track", "Halfpipe", "Terrain Park",
    "Blizzard", "Whiteout", "Frostbite", "Avalanche", "Slushpuppy",
    "Icicle", "Snowflake", "Snowdrift", "Snowpack", "Ice Rink",
    "Yeti", "Bigfoot", "Sasquatch", "Wendigo", "Abominable",
    "Wobble", "Tumble", "Stumble", "Fumble", "Grumble",
    "Noodle", "Pretzel", "Waffle", "Pancake", "Biscuit",
    "Flannel", "Beanie", "Goggle", "Boot", "Binding",
    "Chunder", "Tomahawk", "Scorpion", "Starfish", "Ragdoll",
    "Falls-A-Lot", "Eats-Snow", "Needs-Lessons", "Calls-Mom",
    "Rips-Cord", "Shreds-Gnar", "Sends-It", "Drops-In", "Charges-Hard",
    "Hufflepuff", "Dumbledore", "Gandalf", "Frodo", "Sauron",
    "Sneaky Pete", "Slippery Sam", "Wobbly Bob", "Dizzy Dave", "Frozen Fred",
    "Karen", "Chad", "Brad", "Thad", "Todd",
]

EARTH_SUFFIXES = [
    "Mountain", "Peak", "Summit", "Ridge", "Basin", "Bowl", "Valley",
    "Resort", "Ski Area", "Slopes", "Runs", "Trails", "Heights",
    "Point", "Crest", "Top", "Tip", "Edge", "Ledge", "Cliff",
    "Sanctuary", "Kingdom", "Empire", "Domain", "Territory",
    "Station", "Lodge", "Inn", "Chalet", "Cabin", "Hut",
]

EARTH_STATES = [
    "CO", "UT", "VT", "CA", "WY", "MT", "ID", "WA", "OR", "NV",
    "NM", "AZ", "AK", "NH", "ME", "NY", "WV", "NC", "PA", "MI",
    "MN", "WI", "BC", "QC", "AB", "ON",
    "Bavaria", "Austria", "Switzerland", "Norway", "Sweden", "Finland",
    "Japan", "New Zealand", "Australia", "Scotland", "Andorra",
    "Chile", "Argentina", "Georgia (country)", "Kazakhstan", "Iran",
    "Morocco", "Lebanon", "Turkey", "Romania", "Bulgaria",
]

SPACE_LOCATIONS = [
    "Mars", "Moon", "Europa", "Titan", "Pluto", "Ganymede", "Callisto",
    "Io", "Enceladus", "Triton", "Charon", "Ceres", "Eris", "Makemake",
    "Sedna", "Kepler-22b", "Proxima Centauri b", "TRAPPIST-1e", "TRAPPIST-1f",
    "Andromeda Station Alpha", "NGC-1277 Rim", "Sagittarius A* Outskirts",
    "Betelgeuse Belt", "Crab Nebula", "Horsehead Nebula", "Orion Arm",
    "Virgo Cluster", "Magellanic Cloud", "Kuiper Belt Station 7",
    "Oort Cloud Outpost",
]

SPACE_PREFIXES = [
    "Intergalactic", "Cosmic", "Astro", "Stellar", "Solar", "Lunar",
    "Orbital", "Zero-G", "Low-Gravity", "High-Radiation", "Vacuum",
    "Cryogenic", "Plasma", "Dark Matter", "Antimatter", "Quantum",
    "Wormhole", "Hyperdrive", "Warp Speed", "Subspace", "Hyperspace",
    "Nebular", "Pulsar", "Quasar", "Black Hole", "White Dwarf",
    "Red Giant", "Supernova", "Magnetar", "Neutron Star", "Dark Energy",
    "Ion Storm", "Photon", "Tachyon", "Graviton", "Boson",
    "Interdimensional", "Transdimensional", "Ultradimensional",
    "Galactic", "Extragalactic", "Metagalactic", "Pangalactic",
]

SPACE_NAMES = [
    "Powder Dome", "Crater Bowl", "Regolith Run", "Methane Slopes",
    "Ice Geyser Glades", "Cryovolcano Carve", "Liquid Nitrogen Lanes",
    "Ring System Rips", "Gravity Assist", "Slingshot Slalom",
    "Event Horizon", "Singularity Shred", "Time Dilation Drop",
    "Relativity Ridge", "Dark Side", "Far Side", "Terminator Line",
    "Lagrange Point", "Roche Limit", "Escape Velocity",
    "Baryonic Matter Bowl", "Exotic Particle Park", "Higgs Boson Half-Pipe",
    "Fermi Paradox Flats", "Drake Equation Drops", "Kardashev Scale Kicker",
    "Dyson Sphere Drive", "Von Neumann Neighborhood", "Matrioshka Moguls",
    "Boltzmann Brain Basin", "Heat Death Heights", "Big Crunch Cornice",
    "Big Rip Ridgeline", "Big Bounce Back Bowl", "Ekpyrotic Edge",
    "Holographic Half-Pipe", "Simulation Theory Slalom", "NPC Nursery",
    "Turing Test Terrain", "HAL's Horror Halfpipe", "Skynet Schuss",
    "Matrix Moguls", "Glitch in the Groomer", "Lag Spike Launch",
    "Packet Loss Peak", "Ping Spike Plunge", "Server Error Schuss",
    "404 Slope Not Found", "500 Internal Server Terror", "DNS Lookup Descent",
]

SPACE_SUFFIXES = [
    "Station", "Outpost", "Colony", "Base", "Platform", "Habitat",
    "Dome", "Installation", "Facility", "Complex", "Resort",
    "Sector", "Zone", "District", "Region", "Province", "Territory",
    "Void", "Expanse", "Reaches", "Frontier", "Wilderness",
    "Ski Lodge Alpha", "Snow Dome Beta", "Ice Station Gamma",
    "Powder Depot Delta", "Shred Hub Epsilon", "Gnar Lab Zeta",
]

HAND_CRAFTED = [
    # (name, state, lat, lon, snow_24h, snow_7d)
    ("Mediocre Mountain", "NJ", 40.0, -74.5, 1, 3),
    ("Ski Karen's Peak", "CT", 41.5, -73.1, 3, 12),
    ("Chad's Extremely Dangerous Cliffs", "CO", 39.7, -106.5, 8, 35),
    ("Mount Disappointment", "CA", 34.3, -117.7, 0, 2),
    ("Slightly Uphill Area", "OH", 40.4, -82.9, 0, 1),
    ("Where's the Powder", "VA", 37.4, -79.1, 1, 4),
    ("Ice Rink With Delusions", "FL", 27.9, -82.4, 0, 0),
    ("Fake Snow Fantasy", "TX", 30.3, -97.7, 0, 0),
    ("Mount Overpriced", "VT", 44.5, -72.8, 5, 22),
    ("The Bunny Slope that Never Ends", "NH", 44.0, -71.5, 2, 9),
    ("Lawsuit Gulch", "WY", 43.5, -110.8, 10, 44),
    ("Insurance Claim Bowl", "CO", 39.5, -105.9, 6, 28),
    ("Ambulance Alley", "CA", 37.6, -119.0, 7, 30),
    ("Ski Patrol's Nightmare", "VT", 43.6, -72.8, 4, 18),
    ("The Mogul That Broke My Hip", "MT", 45.3, -111.4, 9, 40),
    ("Lift Line Purgatory", "CO", 39.6, -106.4, 5, 20),
    ("Season Pass Regret", "UT", 40.6, -111.5, 7, 32),
    ("Flat Earth Ski Resort", "ND", 47.0, -100.5, 0, 1),
    ("Mount Hubris", "CO", 39.4, -106.8, 11, 50),
    ("The Double Black That Ate Tourists", "WY", 43.6, -110.9, 14, 60),
    ("Sir Crashes-A-Lot", "Switzerland", 46.5, 7.9, 12, 55),
    ("Herr Doktor Von Snowplow", "Germany", 47.5, 12.9, 8, 36),
    ("Monsieur Le Mogul", "France", 45.8, 6.7, 10, 45),
    ("Baron Von Chairlift", "Austria", 47.2, 12.7, 9, 42),
    ("Tsar Shredovich", "Russia", 43.5, 42.9, 6, 28),
    ("Lord of the Bunny Slopes", "Scotland", 56.8, -3.9, 3, 14),
    ("The Singularity Ski Area (One Way Only)", "NGC-1277 Rim", 0.0, 0.0, 9999, 9999),
    ("Betelgeuse Before It Explodes", "Betelgeuse Belt", 0.5, 0.5, 9000, 60000),
    ("404 Resort Not Found", "Null Island", 0.0, 0.0, 0, 0),
    ("Schrodinger's Ski Slope", "Quantum Foam", 0.0, 0.0, 12, 12),
    ("Elon's Unfinished Mars Resort", "Mars", 4.5, -137.4, 0, 0),
    ("The NFT Ski Lodge (Worthless Now)", "Ethereum-Peak", 40.7, -74.0, 0, 0),
    ("AI-Generated Slope (May Hallucinate)", "Neural Net Nebula", 51.5, -0.1, 6, 6),
    ("Flat Earther's Round Mountain", "Flat Earth", 90.0, 0.0, 0, 0),
    ("Hoth Extreme Winter Sports Complex", "Hoth", -75.0, 0.0, 9999, 9999),
    ("Mustafar Lava Skiing (10/10 Extreme)", "Mustafar", -11.0, 42.0, 0, 0),
    ("Alderaan (It Was Here Yesterday)", "Former Alderaan System", 0.0, 0.0, 0, 0),
    ("Tatooine Twin-Sun Slalom (No Snow)", "Tatooine", 23.0, 53.0, 0, 0),
    ("Endor Ewok-Assisted Chairlift", "Endor", 54.0, -3.0, 12, 66),
    ("Narnia's Perpetual-Winter Resort", "Narnia", 55.0, -2.0, 24, 168),
    ("Winterfell Ski and Slay", "Westeros", 60.0, -5.0, 15, 90),
    ("The Wall (No Lifts North of It)", "Night's Watch HQ", 70.0, 0.0, 50, 350),
    ("Mordor Ash Skiing (Not Recommended)", "Middle Earth, Mordor", 40.0, 28.0, 0, 0),
    ("Hogwarts Quidditch Mountain Annex", "Scotland (Magical)", 57.4, -4.2, 10, 55),
    ("Bikini Bottom Ice Cap", "Pacific Ocean Floor", -20.0, -157.0, 0, 0),
    ("Rock Bottom Resort", "Mariana Trench", -11.4, 142.2, 0, 0),
    ("Olympus Mons Bunny Slope (Its 22km Tall)", "Mars", 18.65, 226.2, 0, 0),
    ("Europa Slushpuppy Express", "Europa", -1.2, 34.5, 3000, 18000),
    ("Enceladus Geyser Halfpipe", "Enceladus", 82.1, 54.3, 5000, 35000),
    ("Space Karen's Galactic Shred Zone", "Virgo Cluster", 10.0, 15.0, 4444, 22222),
]


def random_earth_resort(idx):
    prefix = random.choice(EARTH_PREFIXES)
    mid = random.choice(EARTH_NAMES)
    suffix = random.choice(EARTH_SUFFIXES)
    state = random.choice(EARTH_STATES)
    r = random.random()
    if r < 0.4:
        lat = random.uniform(36, 50)
        lon = random.uniform(-122, -105)
    elif r < 0.6:
        lat = random.uniform(44, 48)
        lon = random.uniform(6, 15)
    elif r < 0.7:
        lat = random.uniform(35, 45)
        lon = random.uniform(136, 145)
    else:
        lat = random.uniform(25, 72)
        lon = random.uniform(-170, 170)
    snow_24h = random.randint(0, 24)
    snow_7d = random.randint(snow_24h, max(snow_24h + 1, random.randint(10, 100)))
    return {
        "name": f"{prefix} {mid} {suffix} #{idx}",
        "state": state,
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "snowfall_24hr_in": snow_24h,
        "snowfall_7day_in": snow_7d,
    }


def random_space_resort(idx):
    location = random.choice(SPACE_LOCATIONS)
    prefix = random.choice(SPACE_PREFIXES)
    mid = random.choice(SPACE_NAMES)
    suffix = random.choice(SPACE_SUFFIXES)
    snow_24h = random.randint(0, 5000)
    snow_7d = random.randint(snow_24h, max(snow_24h + 1, random.randint(1000, 35000)))
    return {
        "name": f"{prefix} {mid} {suffix} #{idx}",
        "state": location,
        "lat": round(random.uniform(-89, 89), 4),
        "lon": round(random.uniform(-179, 179), 4),
        "snowfall_24hr_in": snow_24h,
        "snowfall_7day_in": snow_7d,
    }



resorts = []

for name, state, lat, lon, s24, s7d in HAND_CRAFTED:
    resorts.append({
        "name": name,
        "state": state,
        "lat": round(lat, 4),
        "lon": round(lon, 4),
        "snowfall_24hr_in": s24,
        "snowfall_7day_in": s7d,
    })

remaining = TARGET - len(resorts)
earth_count = int(remaining * 0.6)
space_count = remaining - earth_count

for i in range(earth_count):
    resorts.append(random_earth_resort(i))
for i in range(space_count):
    resorts.append(random_space_resort(i))

random.shuffle(resorts)

print(f"Total resorts generated: {len(resorts)}")

# ---------------------------------------------------------------------------
# Write ski_resorts.json
# ---------------------------------------------------------------------------

with open("gigantic_dataset/ski_resorts.json", "w") as f:
    json.dump({"ski_resorts": resorts}, f, indent=2)

print(f"Written gigantic_dataset/ski_resorts.json")

# Each entry is computed from f(min(i,j), max(i,j)) so no upper-triangle
# storage is needed. Distances are fake but symmetric (dist[i][j]==dist[j][i]).
# Range: 10–4000 miles (intergalactic wormhole routing varies wildly).

def fake_dist(i, j):
    if i == j:
        return 0.0
    a, b = min(i, j), max(i, j)
    h = (a * 1_000_003 + b * 999_983 + a * b * 7) % 1_000_000
    return round(10.0 + (h % 399_001) / 100.0, 2)  # 10–4000 miles

n = len(resorts)
names = [r["name"] for r in resorts]

print(f"Generating {n}x{n} = {n*n:,} distances...")

with open("gigantic_dataset/resort_distances.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([""] + names)
    for i in range(n):
        if i % 500 == 0:
            print(f"  Row {i}/{n}...")
        writer.writerow([names[i]] + [fake_dist(i, j) for j in range(n)])

print("Written gigantic_dataset/resort_distances.csv")