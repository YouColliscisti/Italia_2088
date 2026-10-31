CHARACTER_NAMES = {
    1: "BEATRICE // THE CYBER POET",
    2: "SIMON // THE NEON RUNNER",
    3: "SOFIA // THE GRID SENTINEL",
    4: "ELIAS // THE ANARCHY CORE",
}

OPERATIVE_SHORT_NAMES = {1: "Beatrice", 2: "Simon", 3: "Sofia", 4: "Elias"}

BACKSTORIES = {
    1: {
        "role": "SIGNALS INFILTRATOR // BOLOGNA FREE ARCHIVE",
        "background": "Once a celebrated network poet, Beatrice encoded banned verses inside public data streams. When Omnia erased the Bologna archive—and the identities stored within it—she weaponized her elegant code and built a needle-fast interceptor.",
        "motivation": "She fights to restore Italy's collective memory, proving that culture cannot be owned, indexed, or silenced by a corporate firewall.",
        "connection": "Her pirate broadcasts coordinate archivists, students, and signal runners across the regional resistance. Every node she hacks reopens a channel for their voices.",
    },
    2: {
        "role": "ROOFTOP COURIER // MILAN VELOCITY CELL",
        "background": "Simon delivered medicine through Milan's drone-locked rooftops until a synthetic virus fused his nervous system with his ship. He escaped the corporate clinic, turning their experiment into unmatched speed and twin-cannon agility.",
        "motivation": "He runs so no family has to wait for permission to receive food, medicine, or a warning that could save their lives.",
        "connection": "The resistance's supply routes survive because Simon maps safe corridors in real time and personally escorts the couriers everyone else considers lost.",
    },
    3: {
        "role": "DEFENSE ENGINEER // TURIN WORKERS' COALITION",
        "background": "Sofia maintained Turin's autonomous factories until Omnia converted their workers into disposable assets. She left with an armored Aegis platform and the shield schematics that now protect entire rebel districts.",
        "motivation": "She refuses to mistake survival for freedom. Her mission is to give every community the strength to defend its own future.",
        "connection": "Mechanics, farmers, and displaced factory crews trust her grid because she has stood between their shelters and corporate extermination fleets before.",
    },
    4: {
        "role": "DEMOLITION HACKER // NAPLES BLACKOUT ASSEMBLY",
        "background": "Elias grew up beneath Naples' automated ports, where algorithms decided which neighborhoods received power. A gifted sabotage engineer, he adapted unstable ricochet disks into weapons capable of turning Omnia's infrastructure against itself.",
        "motivation": "He wants more than revenge: he intends to break the centralized systems that make obedience feel unavoidable, even if he must trigger the largest blackout in history.",
        "connection": "His Anarchy Blast is a shared resistance protocol assembled from hundreds of small acts of sabotage across the southern cells.",
    },
}

PROLOGUE_EVENTS = {
    1: [
        ("COMMAND", "Operative Beatrice, the regime has blocked cultural frequencies."),
        ("BEATRICE", "The poetry of the resistance cannot be silenced by a firewall."),
    ],
    2: [
        ("COMMAND", "Runner Simon, patrol drones are locking down the rooftops of Rome."),
        ("SIMON", "I move faster than their algorithms can calculate."),
    ],
    3: [
        ("COMMAND", "Sentinel Sofia, the industrial sector of Turin is under siege."),
        ("SOFIA", "Defense protocols are online. They shall not pass."),
    ],
    4: [
        ("COMMAND", "Elias, the Naples core is surrounded by security forces."),
        ("ELIAS", "Time to blow their digital certainties sky-high."),
    ],
}

BRIEFINGS = {
    1: {
        1: ("Milan Central", "Infiltrate the primary communication node and reopen its outlawed memory archives."),
        2: ("Venice Lagoon", "Guide a resistance supply drone through the flooded corporate checkpoints."),
        3: ("Rome Termini", "Cross the capital while Omnia weaponizes its orbital kinetic defense grid."),
        4: ("Turin Center", "Expose the industrial district hidden beneath a stealth shield network."),
        5: ("Bologna University", "Recover the encryption cores stolen from the historical servers."),
        6: ("Florence Renaissance", "Overload the autonomous surveillance reactors guarding the old city."),
        7: ("Naples Port", "Keep the underground broadcast uplink alive through the final siege."),
        8: ("Omnia Core", "Final assault on the central control mainframe."),
    },
    2: {
        1: ("Rome Roofs", "Hack three clandestine transmission relays before the patrol trace completes."),
        2: ("Florence Skyline", "Escort a medical supply drone across the historic skyline."),
        3: ("Venice Bridges", "Outrun a kinetic storm sweeping through the canal defense grid."),
        4: ("Milan Skyline", "Neutralize the stealth shields concealing the network's central tower."),
        5: ("Turin Roofs", "Recover courier data cores before Omnia's decoy security systems erase them."),
        6: ("Bologna Towers", "Sabotage the aerial reactors powering the district's defenses."),
        7: ("Naples Vesuvius", "Defend the geothermal uplink until the evacuation coordinates transmit."),
        8: ("Omnia Core", "Infiltrate the central surveillance data server."),
    },
    3: {
        1: ("Turin Industries", "Hack local barrier nodes and bring the workers' defense grid online."),
        2: ("Milan Network", "Escort a reactor supply drone through the heavy drone waves."),
        3: ("Bologna Fortress", "Protect the rebel servers while a kinetic storm breaks overhead."),
        4: ("Rome Bastions", "Strip the armored sector of its stealth shield generators."),
        5: ("Venice Dam", "Recover stabilization data from fallen corporate couriers."),
        6: ("Florence Walls", "Sabotage the siege reactors before they breach the old defenses."),
        7: ("Naples Shield", "Cover the resistance retreat by holding the coastal uplink."),
        8: ("Omnia Core", "Lock down the central core with barrier protocols."),
    },
    4: {
        1: ("Underground Naples", "Hack the energy relays and trigger the first citywide overload."),
        2: ("Rome Catacombs", "Escort a munitions drone through the buried corporate checkpoints."),
        3: ("Milan Bunker", "Survive the kinetic barrage aimed at the robotic ammunition depots."),
        4: ("Turin Central", "Expose the EMP control sector by destroying its stealth shields."),
        5: ("Bologna Tunnels", "Retrieve autonomous computing cores from destroyed security couriers."),
        6: ("Florence Inferno", "Cause a cascade failure across four armored reactors."),
        7: ("Venice Arsenal", "Hold the drone assembly uplink while resistance code infects the network."),
        8: ("Omnia Core", "Trigger the final detonation of the OMNIA mainframe."),
    },
}

OBJECTIVES = {
    1: "HACK 3 DATA NODES BEFORE TRACE COMPLETION",
    2: "ESCORT THE RESISTANCE SUPPLY DRONE",
    3: "SURVIVE THE KINETIC STORM",
    4: "NEUTRALIZE THE STEALTH SECTOR SHIELDS",
    5: "RECOVER 5 ENCRYPTED DATA CORES",
    6: "SABOTAGE 4 ARMORED REACTORS",
    7: "DEFEND THE RESISTANCE UPLINK",
    8: "DESTROY ALL OMNIA CORE PHASES",
}

DIALOGUE_DATA = {
    1: ("COMMAND", "The trace window is open. Hold each uplink ring until its node turns green."),
    2: ("COMMAND", "The supply drone has no weapons. Intercept hostile fire and keep its hull intact."),
    3: ("COMMAND", "Kinetic debris is volatile. Shoot it near enemy formations to trigger a shockwave."),
    4: ("COMMAND", "Stealth signatures located. Destroy the three generators to expose the sector."),
    5: ("COMMAND", "Couriers carry the data we need. Collect the yellow cores before they fall away."),
    6: ("COMMAND", "The reactors are armored. Concentrate fire and use debris explosions to clear their escorts."),
    7: ("COMMAND", "This is the last free uplink. Hold the line until the broadcast reaches every sector."),
    8: ("OMNIA CORE", "INTRUSION DETECTED. PHASED ANNIHILATION PROTOCOLS ENGAGED."),
}
