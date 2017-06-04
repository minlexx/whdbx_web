DROP TABLE IF EXISTS signatures;

CREATE TABLE signatures (
    id INT PRIMARY KEY,
    wh_class INT,
    sig_type TEXT,
    sig_name TEXT
);

-- type: combat / data / relic / gas / ore
-- class 1 signatures
INSERT INTO signatures VALUES (1, 1, 'combat', 'Perimeter Ambush Point');
INSERT INTO signatures VALUES (2, 1, 'combat', 'Perimeter Camp');
INSERT INTO signatures VALUES (3, 1, 'combat', 'Phase Catalyst Node');
INSERT INTO signatures VALUES (4, 1, 'combat', 'The Line');
INSERT INTO signatures VALUES (5, 1, 'relic', 'Forgotten Perimeter Coronation Platform');
INSERT INTO signatures VALUES (6, 1, 'relic', 'Forgotten Perimeter Power Array');
INSERT INTO signatures VALUES (7, 1, 'data', 'Unsecured Perimeter Amplifier');
INSERT INTO signatures VALUES (8, 1, 'data', 'Unsecured Perimeter Information Center');
-- class 2 signatures
INSERT INTO signatures VALUES (9, 2, 'combat', 'Perimeter Checkpoint');
INSERT INTO signatures VALUES (10, 2, 'combat', 'Perimeter Hangar');
INSERT INTO signatures VALUES (11, 2, 'combat', 'The Ruins of Enclave Cohort 27');
INSERT INTO signatures VALUES (12, 2, 'combat', 'Sleeper Data Sanctuary');
INSERT INTO signatures VALUES (13, 2, 'relic', 'Forgotten Perimeter Gateway');
INSERT INTO signatures VALUES (14, 2, 'relic', 'Forgotten Perimeter Habitation Coils');
INSERT INTO signatures VALUES (15, 2, 'data', 'Unsecured Perimeter Comms Relay');
INSERT INTO signatures VALUES (16, 2, 'data', 'Unsecured Perimeter Transponder Farm');
-- class 3 signatures
INSERT INTO signatures VALUES (17, 3, 'combat', 'Fortification Frontier Stronghold');
INSERT INTO signatures VALUES (18, 3, 'combat', 'Outpost Frontier Stronghold');
INSERT INTO signatures VALUES (19, 3, 'combat', 'Solar Cell');
INSERT INTO signatures VALUES (20, 3, 'combat', 'The Oruze Construct');
INSERT INTO signatures VALUES (21, 3, 'relic', 'Forgotten Frontier Quarantine Outpost');
INSERT INTO signatures VALUES (22, 3, 'relic', 'Forgotten Frontier Recursive Depot');
INSERT INTO signatures VALUES (23, 3, 'data', 'Unsecured Frontier Database');
INSERT INTO signatures VALUES (24, 3, 'data', 'Unsecured Frontier Receiver');
-- class 4 signatures
INSERT INTO signatures VALUES (25, 4, 'combat', 'Frontier Barracks');
INSERT INTO signatures VALUES (26, 4, 'combat', 'Frontier Command Post');
INSERT INTO signatures VALUES (27, 4, 'combat', 'Integrated Terminus');
INSERT INTO signatures VALUES (28, 4, 'combat', 'Sleeper Information Sanctum');
INSERT INTO signatures VALUES (29, 4, 'relic', 'Forgotten Frontier Conversion Module');
INSERT INTO signatures VALUES (30, 4, 'relic', 'Forgotten Frontier Evacuation Center');
INSERT INTO signatures VALUES (31, 4, 'data', 'Unsecured Frontier Digital Nexus');
INSERT INTO signatures VALUES (32, 4, 'data', 'Unsecured Frontier Trinary Hub');
-- class 5 signatures
INSERT INTO signatures VALUES (33, 5, 'combat', 'Core Garrison');
INSERT INTO signatures VALUES (34, 5, 'combat', 'Core Stronghold');
INSERT INTO signatures VALUES (35, 5, 'combat', 'Oruze Osobnyk');
INSERT INTO signatures VALUES (36, 5, 'combat', 'Quarantine Area');
INSERT INTO signatures VALUES (37, 5, 'relic', 'Forgotten Core Data Field');
INSERT INTO signatures VALUES (38, 5, 'relic', 'Forgotten Core Information Pen');
INSERT INTO signatures VALUES (39, 5, 'data', 'Unsecured Frontier Enclave Relay');
INSERT INTO signatures VALUES (40, 5, 'data', 'Unsecured Frontier Server Bank');
-- class 6 signatures
INSERT INTO signatures VALUES (41, 6, 'combat', 'Core Citadel');
INSERT INTO signatures VALUES (42, 6, 'combat', 'Core Bastion');
INSERT INTO signatures VALUES (43, 6, 'combat', 'Strange Energy Readings');
INSERT INTO signatures VALUES (44, 6, 'combat', 'The Mirror');
INSERT INTO signatures VALUES (45, 6, 'relic', 'Forgotten Core Assembly Hall');
INSERT INTO signatures VALUES (46, 6, 'relic', 'Forgotten Core Circuitry Disassembler');
INSERT INTO signatures VALUES (47, 6, 'data', 'Unsecured Core Backup Array');
INSERT INTO signatures VALUES (48, 6, 'data', 'Unsecured Core Emergence');
-- ore sites
INSERT INTO signatures VALUES (49, 0, 'ore', 'Average Frontier Deposit');
INSERT INTO signatures VALUES (50, 0, 'ore', 'Common Perimeter Deposit');
INSERT INTO signatures VALUES (51, 0, 'ore', 'Exceptional Core Deposit');
INSERT INTO signatures VALUES (52, 0, 'ore', 'Infrequent Core Deposit');
INSERT INTO signatures VALUES (53, 0, 'ore', 'Isolated Core Deposit');
INSERT INTO signatures VALUES (54, 0, 'ore', 'Ordinary Perimeter Deposit');
INSERT INTO signatures VALUES (55, 0, 'ore', 'Rarified Core Deposit');
INSERT INTO signatures VALUES (56, 0, 'ore', 'Unusual Core Deposit');
INSERT INTO signatures VALUES (57, 0, 'ore', 'Uncommon Core Deposit');
INSERT INTO signatures VALUES (58, 0, 'ore', 'Unexceptional Frontier Deposit');
-- gas sites
INSERT INTO signatures VALUES (59, 0, 'gas', 'Barren Perimeter Reservoir');
INSERT INTO signatures VALUES (60, 0, 'gas', 'Bountiful Frontier Reservoir');
INSERT INTO signatures VALUES (61, 0, 'gas', 'Instrumental Core Reservoir');
INSERT INTO signatures VALUES (62, 0, 'gas', 'Minor Perimeter Reservoir');
INSERT INTO signatures VALUES (63, 0, 'gas', 'Ordinary Perimeter Reservoir');
INSERT INTO signatures VALUES (64, 0, 'gas', 'Sizeable Perimeter Reservoir');
INSERT INTO signatures VALUES (65, 0, 'gas', 'Token Perimeter Reservoir');
INSERT INTO signatures VALUES (66, 0, 'gas', 'Vast Frontier Reservoir');
INSERT INTO signatures VALUES (67, 0, 'gas', 'Vital Core Reservoir');

-- Epicenters
INSERT INTO signatures VALUES (70, -1, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (71, -2, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (72, -3, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (73, -4, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (74, -5, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (75, -6, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (76, 13, 'combat', 'Epicenter'); -- frig holes
-- Thera sites
INSERT INTO signatures VALUES (77, 12, 'combat', 'Epicenter');
INSERT INTO signatures VALUES (78, 12, 'combat', 'Expedition Command Outpost Wreck');
INSERT INTO signatures VALUES (79, 12, 'combat', 'Planetary Colonization Office Wreck');
INSERT INTO signatures VALUES (80, 12, 'combat', 'Testing Facilities');
