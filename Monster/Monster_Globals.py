# whocontributes 07/04/2019
# pulled from https://wiki.mabinogiworld.com/index.php?title=Special:WhatLinksHere/Template:StyleMonster&namespace=0&limit=500
FAMILY_PAGES_LIST = ["Bat", "Bear", "Horse","Mimic", "Goblin", "Wolf", "Skeleton", "Golem", "Spider", "Rat", "Snake", "Ogre",
					 "Kobold", "Troll", "Imp", "Succubus", "Wisp", "Flying Sword", "Gremlin", "Werewolf", "Rat Man",
					 "Gargoyle", "Raccoon", "Lycanthrope", "Nightmare Humanoid", "Worm", "Gorgon", "Jackal",
					 "Black Wizard (Monster)", "Cyclops", "Sprite", "Zombie", "Siren (Monster)", "Incubus", "Argus",
					 "Coyote", "Giant Headless", "Boar", "Sahagin", "Gnoll", "Glas Ghaibhleann", "Laghodessa", "Ghost",
					 "Stone Hound", "Stone Zombie", "Stone Horse", "Stone Imp", "Lich", "Cloaker", "Cow (NPC)",
					 "Mongoose", "Aardvarks", "Kiwi", "Gnu", "Lizard", "Banshees", "Horse", "Slate", "Cat", "Lion",
					 "Elephant", "Llama", "Armadillos", "Stone Horse Keeper", "Dark Lord", "Mask", "Dragon", "Ifrit",
					 "Python", "Skeleton Wolf", "Hyena", "Wendigo", "Specter Army", "Bison", "Ant Lions", "Wasp",
					 "Scorpion", "Desert Ghost", "Stone Gargoyle", "Grendel", "Cobra", "Penguin", "Ostrich",
					 "Porcupine", "Elf Guard", "Giant Guard", "Lynx", "Dog", "Bandersnatch", "Rhino", "Saturos",
					 "Buffalo", "Witch", "Ostrich (NPC)", "Living Armor", "Pot-Belly Spider", "Salamander",
					 "Horse (NPC)", "Sheep (NPC)", "Sarracenia", "Mammoth", "Yeti", "Guardian of Ruins", "Lungfish",
					 "Millipede", "Chon Chon", "Wyvern", "Dingo", "Warg", "Jewel Beetle", "Spider Humanoid", "Larva",
					 "Ice Worm (NPC)", "Hedgehog (NPC)", "Succubus Kristell", "Castle Warrior", "Ice Bear", "Shrieker",
					 "Bisque Doll", "Event Monsters", "Cotton Candy Sheep (Event)", "Alligators", "Tarantula",
					 "Carnivorous Plant", "Dragonfly", "Cat Humanoid", "Hippo (NPC)", "Hobgoblin", "Hippo", "Rabbit",
					 "Fox", "Leopard", "Stag Beetle", "Crab", "Anteater", "Neid", "Ixion", "Chicken (NPC)",
					 "Zebra (NPC)", "Otter (NPC)", "Dog (NPC)", "Monkey (NPC)", "Capybara", "Deer (Monster)", "Balrogs",
					 "Skeleton (Hard Mode)", "Question and Answer/Archive3 ‎ (← links | edit)", "Alchemists (Enemy)",
					 "Sheep", "Goat (NPC)", "Dullahan", "Temple Knight", "Bunting (NPC)", "Cat (NPC)", "Mouse",
					 "Giant Moon Bunny (Event)", "Mini Milk Cow (Event)", "Deer (NPC)", "Crow (NPC)", "Lucas (Monster)",
					 "Pigeon (NPC)", "Butterfly", "Moth", "Aonbharrs", "Ghast", "Lebbaeus (Monster)",
					 "Ruairi (Monster)", "Training Monsters", "Booby (NPC)", "Iguana (NPC)", "Triona (Monster)",
					 "Rabbit (NPC)", "Hornet", "Giant Brown Hawk", "Event Monsters/Spirit Caravan Event",
					 "Event Monsters/Lorraine's Nightmare Event", "(Skilled Mage) Stewart",
					 "(Apprentice Holy Knight) Secretive Knightage", "(Master Alchemist) Dorren",
					 "(Master Fighter) Argel", "Giant White Snowfield Bear", "Chess Piece",
					 "(Master Romantic Chef) Glewyas", "Raptor", "Duke (Monster)", "Sephirot",
					 "(Wise Musical Child Prodigy) Goblin Bard", "(Champion Fighter) Giant Fighter", "Cor Villagers",
					 "Shinobi", "Esras (Monster)", "Event Monsters/Constellation Event",
					 "Event Monsters/Cookie Island Event", "Spirit of Jabchiel", "Form of Chaos", "Mokkurkalfi",
					 "Elf Archer", "(Master Archer) Granat", "(Apprentice Addicted Archer) Granites",
					 "(Master Executioner) Krug", "Giant Knight", "(Master Cleric) Comgan", "(Seasoned Cleric) Agnes",
					 "(Master Musician) Briana", "Form of Awakening", "Skelemancer", "Dailies Guide",
					 "(Amateur Student) Lassar", "(Amateur Warlord) Andras", "(Apprentice Commander) Tethra",
					 "(Apprentice Holy Knight) Collen", "(Apprentice Mage) Galvin", "(Apprentice Sailor) Admiral Owen",
					 "(Apprentice Sharp Shooter) Riocard", "(Fledgling Blacksmith) Ferghus",
					 "(Fledgling Battle Alchemist) Heledd", "(Master Battle Alchemist) Eabha",
					 "(Master Battle Alchemist) Heledd", "(Master Blacksmith) Edern", "(Master Brawler) Cecilia",
					 "(Master Gourmet) Beggar", "(Master Maid) Older Girl Next Door", "(Master Orfevre) Walter",
					 "(Master of Reading) Arzhela", "(Master Ranger) Waboka", "(Master Vagabond) Price",
					 "(Seasoned Flower Merchant) Del", "(Senior Vanguard) Nerys", "(Skilled Minor) Sion",
					 "(Skilled Vanguard) Aranwen", "(Wise Fighter) Goblin Fighter", "(Master Tailor) Simon",
					 "(Amateur Conqueror) Black Knight", "Soldier Knight", "(Apprentice Bard) Nele",
					 "(Apprentice Troubadour) Sinead", "(Master Shaman) Kousai", "(Master of the Beasts) Ruwai",
					 "(Master of the Single Life) Bryce", "(Apprentice Warrior in Crush) Padan",
					 "(Amateur Warrior) Trefor", "Angry Bear", "(Master Druid) Tarlach", "(Amateur Druid) Berched",
					 "(Master Vanguard) Lileas", "(Amateur Repairer) Jennifer", "(Apprentice Home Economist) Taunes",
					 "(Master Addicted Archer) Annick", "(Master Addicted Swordsman) Lucas",
					 "(Master Dog Fighter) Fleta", "(Master Marksman) Drone", "(Master Shepherd Fighter) Deian",
					 "(Master Warrior) Aodhan"]
# pulled from https://wiki.mabinogiworld.com/view/Property:Monster_skills
VALID_SKILLS = ["Abyss Judgement", "Abyss Snare", "Abyss Terror", "Act 1: Inciting Incident", "Act 2: Threshold Cutter",
				"Act 4: Rising Action", "Act 6: Crisis", "Act 7: Climactic Crash", "Act 9: Invigorating Encore",
				"Actions", "Advanced Heavy Stander", "Alban Golem Ambush", "Alban Golem Gatling",
				"Alban Golem Ice Slip", "Alchemy Mastery", "Anchor Rush", "Armor of Connous", "Arrow Revolver",
				"Artifact Investigation", "Assault Slash", "Awakening of Light", "Axe Mastery", "Axe Throwing",
				"Bachram Explosion", "Barrier Spikes", "Bash", "Battlefield Overture", "Beast", "Beast Roar",
				"Beholder Beam Attack", "Berserk", "Bewilder", "Binding Needle", "Black Dragon's Breath",
				"Blacksmithing", "Blaze", "Blink", "Blunt Mastery", "Body of Chaos", "Bolt Mastery",
				"Bolt Out of the Blue (Monster)", "Boost", "Bow Mastery", "Bran's Arm Swing", "Bran's Charge",
				"Bran's Shockwave", "Breaking Lies", "Breath of Ladeca", "Bubble Blast", "Bullet Slide", "Bullet Storm",
				"Burnout", "Campfire", "Carpentry", "Catering", "Celestial Spike", "Chain Blade Mastery", "Chain Burst",
				"Chain Casting (Monster)", "Chain Crush", "Chain Cylinder", "Chain Impale", "Chain Sweep", "Charge",
				"Charge (Pet)", "Charging Strike", "Christening Blades", "Cleansing Dust",
				"Close-quarters Sandworm Attack", "Colossus Marionette", "Combat Mastery", "Combo Mastery",
				"Combo: Counter Punch", "Commerce Mastery", "Compose", "Connous Heavy Stander",
				"Connous Mana Deflector", "Connous Natural Shield", "Control Marionette", "Control of Darkness",
				"Cooking", "Counterattack", "Crash Shot", "Create Falias Portal", "Crisis Escape", "Critical Hit",
				"Crossbow Mastery", "Curse of Devil", "Daemon of Physis", "Dance Time", "Dance of Death",
				"Dark Heavy Stander", "Dark Knight", "Dark Knight Quest", "Dark Mana Deflector", "Dark Natural Shield",
				"Death Mark", "Deepening Trust", "Defense", "Demigod", "Detection", "Devil's Cry", "Devil's Dash",
				"Dischord", "Divine Blast", "Divine Liberty", "Divine Link", "Divinity", "Doppelganger", "Dorcha",
				"Dorcha Conversion", "Dorcha Mastery", "Dorcha Snatch", "Double-Edged Swing", "Dragon Fireball",
				"Dragon Rage", "Drop Kick", "Dual Gun Mastery", "Dual Wield Mastery", "Duke's Kiss", "Duke's Mist",
				"Duke's Rose", "Duke's Temptation", "Earth Alchemy Mastery", "Earth Dragon Roar", "Egg Gathering",
				"Elemental Wave", "Elf Ranged Attack", "Elven Magic Missile", "Enchant", "Encore", "Enduring Melody",
				"Enlightened Vision", "Enthralling Performance", "Enuma Elish", "Evasion", "Excalibur",
				"Exploration Mastery", "Explosive Kunai", "Eye of Order", "Falcon", "Fanaticism", "Fantastic Chorus",
				"Fast Regeneration", "Fierce Charge", "Final Hit", "Final Shot", "Final Strike", "Fire Alchemy",
				"Fire Breath", "Fire Mastery", "Fire Shield", "Fire Storm", "Fireball", "Firebolt", "First Aid",
				"Fishing", "Flame Burst", "Flame Dive", "Flame of Resurrection", "Flames of Hell", "Flash Launcher",
				"Flight (Monster Skill)", "Focused Fist", "Fragmentation", "Freeze! Stop Right There!", "Frost Blade",
				"Frozen Blast", "Fury of Connous", "Fury of Light", "Fusion Bolt", "Gathering", "Generation 2: Paladin",
				"Ghost Voice", "Giant Full Swing", "Giving Heart", "Glas Ghaibhleann Skill", "God Hand: Twelve Labors",
				"Gold Strike", "Golden Time", "Grapple Shot", "Grim Reaper Horizontal Attack",
				"Grim Reaper Vertical Attack", "Grim Reaper Windmill", "Grudge of Tuan", "Guard Cylinder Mastery",
				"Guarded Footsteps", "Guardian Oath", "Hail Storm", "Handicraft", "Hands of Chaos",
				"Hands of Salvation", "Harvest Song", "Harvesting", "Healing", "Healing Breeze", "Healing Hands",
				"Healing Wind", "Heat Buster", "Heavy Armor Mastery", "Heavy Stander", "Herbalism",
				"Hillwen Engineering", "Hoeing", "Holy Confinement", "Holy Contagion", "Holy Rampage", "Holy Rush",
				"Holy Shower", "Holy Vitality", "Hop In", "Hop Shield", "Hop Spin", "Human Ranged Attack",
				"Hydra Transmutation", "Ice Breath", "Ice Hold", "Ice Mastery", "Ice Shield", "Ice Spear", "Ice Storm",
				"Icebolt", "Ingredient Hunting", "Inspiration", "Instinctive Reaction", "Invisible Air",
				"Invitation of Death", "Invulnerability", "Jack's Frozen Field", "Jack's Garden",
				"Jack's Throw Snowball", "Judgment Blade", "Jump", "King's Treasure", "Knuckle Mastery",
				"Kokopo Strike", "Kokopo Wave", "Kunai Storm", "Lance Charge", "Lance Counter", "Lance Mastery",
				"Life Drain", "Life Drain (Monster)", "Life of Physis", "Light Armor Mastery", "Light of Sword",
				"Lightning Bolt", "Lightning Breath", "Lightning Mastery", "Lightning Rod", "Lightning Shield",
				"Lost and Found (Skill)", "Lullaby", "Magic Craft", "Magic Dampening", "Magic Fusion", "Magic Mastery",
				"Magic Weapon Mastery", "Magnum Shot", "Mana Crystallization", "Mana Deflector", "Mana Drain",
				"Mana Shield", "March Song", "Master Teleport", "Meditation", "Merrow Rising Dragon",
				"Merrow Tidal Wave", "Metal Conversion", "Metallurgy", "Meteor", "Meteor Strike", "Might of Ladeca",
				"Milking", "Mind of Chaos", "Mind of Connous", "Mineral Explosion", "Mineral Hail", "Mini Jack",
				"Mining", "Mirage Missile", "Mushroom Gathering", "Musical Knowledge", "Nascent Divinity",
				"Natural Shield", "Natural Shield (Monster)", "Night Change", "Nova Obliteration", "Paladin",
				"Paladin Heavy Stander", "Paladin Mana Deflector", "Paladin Natural Shield", "Palalan Embrace",
				"Paper Airplane Bomb", "Party Healing", "Passive Defense", "Pet Teleport", "Petrification",
				"Petrifying Roar", "Phantom Roar", "Physis Heavy Stander", "Physis Mana Deflector",
				"Physis Natural Shield", "Pierrot Marionette", "Playing Instrument", "Poison Attack", "Potion Making",
				"Power of Order", "Produce Cobweb", "Production Mastery", "Pummel", "Puppet's Snare", "Purgatory",
				"Rage Impact", "Raging Spike", "Rain Casting", "Rain of Thunder", "Rare Mineralogy", "Recovering Touch",
				"Red Dragon Fire Breath", "Refining", "Reflective Damage", "Reload", "Respite", "Rest", "Restful Wind",
				"Roar", "Roar (Monster)", "Running Boost", "Sacred Revival", "Sakura Abyss", "Sand Burst",
				"Save Location", "Scarecrow Curse", "Self-Destruct", "Shadow Bind", "Shadow Cloak", "Shadow Death",
				"Shadow Spirit", "Sharp Mind", "Sharpness of Connous", "Sheep Shearing", "Shield Mastery",
				"Shield of Physis", "Shield of Trust", "Shine of Eweca", "Shock", "Shockwave", "Shooting Rush",
				"Shuriken Charge", "Shuriken Mastery", "Shyllien Ecology", "Sinful Thorns", "Skills List (Elf)",
				"Skills List (Giant)", "Skills List (Human)", "Sleepy Dust", "Smack", "Smash", "Smokescreen",
				"Snap Cast", "Snow Bomb", "Somersault Kick", "Song", "Soul Absorption", "Soul Chase",
				"Soul Restoration", "Soul of Chaos", "Spear of Light", "Spell of Physis", "Spellwalk", "Spider Shot",
				"Spinning Slash", "Spinning Slasher", "Spinning Uppercut", "Spirit Weapon Awakening", "Spirit of Order",
				"Spreading Faith", "Staff Swing", "Stampede", "Stats and Skills", "Stomp", "Stomp (Monster)",
				"Stronger Power", "Study: Potion Lore", "Summon Golem", "Summon Monster", "Support Shot", "Swallow",
				"Sword Mastery", "Sword of Order", "Synthesis", "Tail Attack", "Tailoring", "Taming Wild Animals",
				"Tasting", "Taunt", "Teleportation", "The Fake Spiral Sword", "Throwing Attack", "Thunder",
				"Thunder Breath", "Thunder Storm", "Tiny Jibes", "Transformation Mastery", "Transformations",
				"Transmutation", "Trial of Pain", "Truck to the Head", "Tumble", "Unlimited Blade Works", "Urgent Shot",
				"Vision of Ladeca", "Vivace", "Water Alchemy", "Water Cannon", "Water Spray", "Way of the Gun",
				"Weaving", "Weighed Conscience", "Whisper of Tuan", "White Dragon's Breath", "Wind Alchemy",
				"Wind Blast", "Wind Guard", "Windmill", "Wine Making", "Wings of Eclipse", "Wings of Rage", "Wire Pull",
				"Wool of the Gods", "Wounding Soul"]
SKILL_BLACKLIST = ['HeavyStander', 'ManaDeflector', 'NaturalShield', 'None']
CAPITIAL_EACH_WORD = ["Speed", "Element", "AggroRange", "AggroSpeed"]
