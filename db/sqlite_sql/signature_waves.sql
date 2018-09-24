DROP TABLE IF EXISTS signature_waves;

CREATE TABLE signature_waves (
    sig_id INT,
    wave_id INT,
    is_capital INT,
    sleepers TEXT
);

-- sleepers: 'sleeper_id:count:abilities,sleeper_id:count:abilities'

-- class 1 sigs
-- 1 - Perimeter Ambush Point
INSERT INTO signature_waves VALUES (1, 1, 0, '11:2,7:1:t,10:1:w');
INSERT INTO signature_waves VALUES (1, 2, 0, '7:2:t,8:3');
INSERT INTO signature_waves VALUES (1, 3, 0, '5:2,7:2');
-- 2 - Perimeter Camp
INSERT INTO signature_waves VALUES (2, 1, 0, '11:2,9:2:nt,8:4');
INSERT INTO signature_waves VALUES (2, 2, 0, '9:3:n,8:5,5:1:t');
INSERT INTO signature_waves VALUES (2, 3, 0, '8:2,5:2,6:1:n');
-- 3 - Phase Catalyst Node
INSERT INTO signature_waves VALUES (3, 1, 0, '11:4,9:4,10:2:wt');
INSERT INTO signature_waves VALUES (3, 2, 0, '5:2,7:1:t');
INSERT INTO signature_waves VALUES (3, 3, 0, '8:6,9:3:n');
-- 4 - The Line
INSERT INTO signature_waves VALUES (4, 1, 0, '9:3:n,8:4,6:1:nt');
INSERT INTO signature_waves VALUES (4, 2, 0, '10:3:w,5:2:t');
INSERT INTO signature_waves VALUES (4, 3, 0, '6:5:n');
-- 5 - Forgotten Perimeter Coronation Platform
INSERT INTO signature_waves VALUES (5, 1, 0, '5:2,10:1:w,8:2:t');
INSERT INTO signature_waves VALUES (5, 2, 0, '5:3:t,10:1:w');
INSERT INTO signature_waves VALUES (5, 3, 0, '6:3:n,5:2,8:3');
-- 6 - Forgotten Perimeter Power Array
INSERT INTO signature_waves VALUES (6, 1, 0, '5:2:t');
INSERT INTO signature_waves VALUES (6, 2, 0, '7:2:t,9:3:n');
INSERT INTO signature_waves VALUES (6, 3, 0, '7:2,6:2:n');
-- 7 - Unsecured Perimeter Amplifier
INSERT INTO signature_waves VALUES (7, 1, 0, '5:2:t');
INSERT INTO signature_waves VALUES (7, 2, 0, '9:3:n,7:3:t');
INSERT INTO signature_waves VALUES (7, 3, 0, '7:2,6:2:n');
-- 8 - Unsecured Perimeter Information Center
INSERT INTO signature_waves VALUES (8, 1, 0, '8:3,9:1:n,5:1:t');
INSERT INTO signature_waves VALUES (8, 2, 0, '9:1,5:3:t');
INSERT INTO signature_waves VALUES (8, 3, 0, '5:2,6:3:n,8:2');

-- class 2 sigs
-- 9 - Perimeter Checkpoint
INSERT INTO signature_waves VALUES (9, 1, 0, '11:2,5:3:t,8:2');
INSERT INTO signature_waves VALUES (9, 2, 0, '5:2:t,7:2:w');
INSERT INTO signature_waves VALUES (9, 3, 0, '1:1,8:2');
-- 10 - Perimeter Hangar
INSERT INTO signature_waves VALUES (10, 1, 0, '5:3:t,9:2:n');
INSERT INTO signature_waves VALUES (10, 2, 0, '2:1,7:2:t');
INSERT INTO signature_waves VALUES (10, 3, 0, '3:1,7:2');
-- 11 - The Ruins of Enclave Cohort 27
INSERT INTO signature_waves VALUES (11, 1, 0, '1:1,8:6:t');
INSERT INTO signature_waves VALUES (11, 2, 0, '5:5:t,9:1:n');
INSERT INTO signature_waves VALUES (11, 3, 0, '3:1');
-- 12 - Sleeper Data Sanctuary
INSERT INTO signature_waves VALUES (12, 1, 0, '11:3,7:2:t,8:3');
INSERT INTO signature_waves VALUES (12, 2, 0, '3:1:t,10:5:w');
INSERT INTO signature_waves VALUES (12, 3, 0, '3:1:t');
INSERT INTO signature_waves VALUES (12, 4, 0, '4:1:n');
-- 13 - Forgotten Perimeter Gateway
INSERT INTO signature_waves VALUES (13, 1, 0, '5:4,6:1:nt');
INSERT INTO signature_waves VALUES (13, 2, 0, '1:1,9:2:nt');
INSERT INTO signature_waves VALUES (13, 3, 0, '3:1,2:1,8:4');
-- 14 - Forgotten Perimeter Habitation Coils
INSERT INTO signature_waves VALUES (14, 1, 0, '5:3,10:2:wt,8:2');
INSERT INTO signature_waves VALUES (14, 2, 0, '5:4:t,10:4:w');
INSERT INTO signature_waves VALUES (14, 3, 0, '1:1:t,10:4:w,8:4');
INSERT INTO signature_waves VALUES (14, 4, 0, '2:1,5:1,7:2,10:3:w');
-- 15 - Unsecured Perimeter Comms Relay
INSERT INTO signature_waves VALUES (15, 1, 0, '5:2,6:2:nt,4:1:n');
INSERT INTO signature_waves VALUES (15, 2, 0, '1:1:t,9:2:n');
INSERT INTO signature_waves VALUES (15, 3, 0, '2:1,3:1,8:2');
-- 16 - Unsecured Perimeter Transponder Farm
INSERT INTO signature_waves VALUES (16, 1, 0, '5:3,8:1,10:2:wt');
INSERT INTO signature_waves VALUES (16, 2, 0, '6:1:n,5:4:t,10:2:w');
INSERT INTO signature_waves VALUES (16, 3, 0, '1:1,8:4,10:4:w');
INSERT INTO signature_waves VALUES (16, 4, 0, '5:5,7:3,10:4:w');

-- class 3 sigs
-- 17 - Fortification Frontier Stronghold
INSERT INTO signature_waves VALUES (17, 1, 0, '16:2:t,19:2:w');
INSERT INTO signature_waves VALUES (17, 2, 0, '17:2:wnt,16:2');
INSERT INTO signature_waves VALUES (17, 3, 0, '13:1:n,16:2,17:1:wn,18:1:rZ');
-- 18 - Outpost Frontier Stronghold
INSERT INTO signature_waves VALUES (18, 1, 0, '22:3,12:1:wt');
INSERT INTO signature_waves VALUES (18, 2, 0, '16:4:t');
INSERT INTO signature_waves VALUES (18, 3, 0, '19:4:w,12:2:wZ');
-- 19 - Solar Cell
INSERT INTO signature_waves VALUES (19, 1, 0, '17:1:wn,21:1:wndt,12:1:wR');
INSERT INTO signature_waves VALUES (19, 2, 0, '17:1:wn,16:3,19:2:w,20:2:nrt');
INSERT INTO signature_waves VALUES (19, 3, 0, '14:1:rZ,12:1:w,16:2');
-- 20 - The Oruze Construct
INSERT INTO signature_waves VALUES (20, 1, 0, '22:2,18:1:rR,17:4:wnt');
INSERT INTO signature_waves VALUES (20, 2, 0, '12:1:wt,19:4:w');
INSERT INTO signature_waves VALUES (20, 3, 0, '13:1:n,18:2:rZ');
-- 21 - Forgotten Frontier Quarantine Outpost
INSERT INTO signature_waves VALUES (21, 1, 0, '18:3:rt,19:6:w');
INSERT INTO signature_waves VALUES (21, 2, 0, '17:2:wn,16:3:t,18:2:r');
INSERT INTO signature_waves VALUES (21, 3, 0, '12:1:w,20:4:nrt');
INSERT INTO signature_waves VALUES (21, 4, 0, '14:2:r,19:4:w');
-- 22 - Forgotten Frontier Recursive Depot
INSERT INTO signature_waves VALUES (22, 1, 0, '21:4:wnd,16:2:t');
INSERT INTO signature_waves VALUES (22, 2, 0, '16:3:t,17:4:wn');
INSERT INTO signature_waves VALUES (22, 3, 0, '19:2:w,17:2:wn,13:2:nt');
INSERT INTO signature_waves VALUES (22, 4, 0, '21:2:wnd,17:1:wn,13:3:n');
-- 23 - Unsecured Frontier Database
INSERT INTO signature_waves VALUES (23, 1, 0, '16:3,21:3:wndt');
INSERT INTO signature_waves VALUES (23, 2, 0, '17:4:wn,16:4:t');
INSERT INTO signature_waves VALUES (23, 3, 0, '13:1:nt,17:3:wn,19:3:w');
INSERT INTO signature_waves VALUES (23, 4, 0, '13:2:n,17:3:wn,21:2:wnd');
-- 24 - Unsecured Frontier Receiver
INSERT INTO signature_waves VALUES (24, 1, 0, '19:5:w,18:3:rt');
INSERT INTO signature_waves VALUES (24, 2, 0, '16:3,18:1:rt,17:3:wn');
INSERT INTO signature_waves VALUES (24, 3, 0, '20:4:nr,12:1:wt');
INSERT INTO signature_waves VALUES (24, 4, 0, '19:4:w,14:2:r');

-- class 4 sigs
-- 25 - Frontier Barracks
INSERT INTO signature_waves VALUES (25, 1, 0, '13:1:n,14:1:rt');
INSERT INTO signature_waves VALUES (25, 2, 0, '18:2:r,13:3:nt');
INSERT INTO signature_waves VALUES (25, 3, 0, '21:3:wnd,18:4:r,14:3:r');
-- 26 - Frontier Command Post
INSERT INTO signature_waves VALUES (26, 1, 0, '22:5,19:4:w,21:4:wndt');
INSERT INTO signature_waves VALUES (26, 2, 0, '20:4:nr,16:6:t,12:2:w');
INSERT INTO signature_waves VALUES (26, 3, 0, '14:3:r,16:2,18:2:r');
-- 27 - Integrated Terminus
INSERT INTO signature_waves VALUES (27, 1, 0, '22:4,16:4:t,20:3:nr');
INSERT INTO signature_waves VALUES (27, 2, 0, '18:2:r,17:4:wnt,21:2:wnd');
INSERT INTO signature_waves VALUES (27, 3, 0, '19:4:w,20:2:nr,15:1:wnd');
-- 28 - Sleeper Information Sanctum
INSERT INTO signature_waves VALUES (28, 1, 0, '17:2:wn,14:2:t,20:2:nr');
INSERT INTO signature_waves VALUES (28, 2, 0, '12:3:w,15:1:wndt');
INSERT INTO signature_waves VALUES (28, 3, 0, '18:2:r,17:2:wn,21:2:wnd,20:3:nr');
-- 29 - Forgotten Frontier Conversion Module
INSERT INTO signature_waves VALUES (29, 1, 0, '22:1,19:6:w,16:6,13:1');
INSERT INTO signature_waves VALUES (29, 2, 0, '19:5:w,16:5,12:3:wt');
INSERT INTO signature_waves VALUES (29, 3, 0, '15:4:wnd');
-- 30 - Forgotten Frontier Evacuation Center
INSERT INTO signature_waves VALUES (30, 1, 0, '19:4:w,14:1:rt');
INSERT INTO signature_waves VALUES (30, 2, 0, '16:4,14:2:rt');
INSERT INTO signature_waves VALUES (30, 3, 0, '12:2:w,14:2:r');
-- 31 - Unsecured Frontier Digital Nexus
INSERT INTO signature_waves VALUES (31, 1, 0, '19:4:w,16:6:t');
INSERT INTO signature_waves VALUES (31, 2, 0, '21:4:wnd,16:4,12:3:wt');
INSERT INTO signature_waves VALUES (31, 3, 0, '15:4:wnd');
-- 32 - Unsecured Frontier Trinary Hub
INSERT INTO signature_waves VALUES (32, 1, 0, '19:4:w,14:1:rt');
INSERT INTO signature_waves VALUES (32, 2, 0, '16:4,14:2:rt');
INSERT INTO signature_waves VALUES (32, 3, 0, '12:2:w,14:2:r');

-- Class 5 --
-- Core Garrrison --
INSERT INTO signature_waves VALUES (33, 1, 0, '33:3,30:5:wd,27:5:wt');
INSERT INTO signature_waves VALUES (33, 2, 0, '31:6:nrt,23:3:wnd');
INSERT INTO signature_waves VALUES (33, 3, 0, '27:5:wD,28:3:wnd,23:3:wndt');
INSERT INTO signature_waves VALUES (33, 4, 0, '32:3:wnd,27:2:w,24:2:n');
INSERT INTO signature_waves VALUES (33, 1, 1, '101:3:wns');
-- Core Stronghold --
INSERT INTO signature_waves VALUES (34, 1, 0, '33:6,30:4:wdt');
INSERT INTO signature_waves VALUES (34, 2, 0, '24:2:n,25:2:rt');
INSERT INTO signature_waves VALUES (34, 3, 0, '32:6:wnd,27:7:wt');
INSERT INTO signature_waves VALUES (34, 4, 0, '29:4:r,24:2:nD,25:3:r');
INSERT INTO signature_waves VALUES (34, 1, 1, '101:3:wns');
-- Oruze Osobnyk --
INSERT INTO signature_waves VALUES (35, 1, 0, '30:4:wd,24:1:nR,23:3:wndt');
INSERT INTO signature_waves VALUES (35, 2, 0, '27:6:w,26:1:wndt');
INSERT INTO signature_waves VALUES (35, 3, 0, '31:4:nrD,32:2:wnd,29:3:r');
INSERT INTO signature_waves VALUES (35, 1, 1, '101:3:wns');
-- Quarantine Area --
INSERT INTO signature_waves VALUES (36, 1, 0, '33:4,10:3:w,28:2:wnd,23:1:wnd');
INSERT INTO signature_waves VALUES (36, 2, 0, '27:4:w,23:2:wnd');
INSERT INTO signature_waves VALUES (36, 3, 0, '30:5:wd,29:3:r,24:2:nD');
INSERT INTO signature_waves VALUES (36, 1, 1, '101:3:wns');

-- Forgotten Core Data Field --
INSERT INTO signature_waves VALUES (37, 1, 0, '30:5:wd,28:5:wndt');
INSERT INTO signature_waves VALUES (37, 2, 0, '31:4:nr,32:4:wnd,28:3:wndt,27:2:w,29:3:r');
INSERT INTO signature_waves VALUES (37, 3, 0, '32:5:wnd,24:2:nt,23:2:wnd');
INSERT INTO signature_waves VALUES (37, 4, 0, '28:2:wnd,29:2:r,24:2:n,25:2:r');
INSERT INTO signature_waves VALUES (37, 1, 1, '101:3:wns');
-- Forgotten Core Information Pen --
INSERT INTO signature_waves VALUES (38, 1, 0, '24:3:nt,24:1:nR');
INSERT INTO signature_waves VALUES (38, 2, 0, '31:4:nr,29:4:r,24:2:n');
INSERT INTO signature_waves VALUES (38, 3, 0, '31:3:nr,32:3:wnd,27:3:w,29:4:rt,24:3:n');
INSERT INTO signature_waves VALUES (38, 4, 0, '32:4:wnd,28:4:wnd,24:5:n');
INSERT INTO signature_waves VALUES (38, 1, 1, '101:3:wns');
-- Unsecured Frontier Enclave Relay --
INSERT INTO signature_waves VALUES (39, 1, 0, '24:3:nt');
INSERT INTO signature_waves VALUES (39, 2, 0, '31:5:nr,29:4:r,24:2:nt');
INSERT INTO signature_waves VALUES (39, 3, 0, '31:3:nr,32:4:wnd,27:3:w,29:4:r,24:2:nt');
INSERT INTO signature_waves VALUES (39, 4, 0, '32:3:wnd,29:3:r,25:5:r');
INSERT INTO signature_waves VALUES (39, 1, 1, '101:3:wns');
-- Unsecured Frontier Server Bank --
INSERT INTO signature_waves VALUES (40, 1, 0, '30:5:wd,28:5:wndt');
INSERT INTO signature_waves VALUES (40, 2, 0, '31:3:nr,32:3:wnd,28:4:wndt,27:2:w,29:4:r');
INSERT INTO signature_waves VALUES (40, 3, 0, '32:5:wnd,24:2:nt,23:1:wnd');
INSERT INTO signature_waves VALUES (40, 4, 0, '28:2:wnd,29:3:r,24:2:n,25:2:r');
INSERT INTO signature_waves VALUES (40, 1, 1, '101:3:wns');

-- class 6 sigs
-- 41 - Core Citadel
INSERT INTO signature_waves VALUES (41, 1, 0, '24:1:n,23:1:wnd,25:1:rt');
INSERT INTO signature_waves VALUES (41, 2, 0, '31:8:nr,23:3:wnd,25:1:rt');
INSERT INTO signature_waves VALUES (41, 3, 0, '31:8:nr,24:3:nt,25:3:r');
INSERT INTO signature_waves VALUES (41, 4, 0, '31:6:nrD,26:2:wnd');
INSERT INTO signature_waves VALUES (41, 1, 1, '101:4:wns');
-- 42 - Core Bastion
INSERT INTO signature_waves VALUES (42, 1, 0, '33:3,31:3:nrt,30:3:w,28:3:wnd,27:3:w,29:3:r,23:2:wnd');
INSERT INTO signature_waves VALUES (42, 2, 0, '27:4:w,29:4:rt,24:4:n');
INSERT INTO signature_waves VALUES (42, 3, 0, '32:6:wnd,29:5:r,26:4:wndt');
INSERT INTO signature_waves VALUES (42, 4, 0, '26:2:wndD,23:4:wnd');
INSERT INTO signature_waves VALUES (42, 1, 1, '101:4:wns');
-- 43 - Strange Energy Readings
INSERT INTO signature_waves VALUES (43, 1, 0, '31:5:nr,29:5:rt,24:2:n');
INSERT INTO signature_waves VALUES (43, 2, 0, '28:6:wnd,26:3:wndt');
INSERT INTO signature_waves VALUES (43, 3, 0, '31:6:nr,29:4:r,24:5:n');
INSERT INTO signature_waves VALUES (43, 1, 1, '101:4:wns');
-- 44 - The Mirror
INSERT INTO signature_waves VALUES (44, 1, 0, '33:6,32:6:wnd,29:4:r,23:2:wnd,25:3:rt');
INSERT INTO signature_waves VALUES (44, 2, 0, '30:6:wd,24:2:n,26:3:wndt');
INSERT INTO signature_waves VALUES (44, 3, 0, '31:4:nr,32:4:wnd,28:4:wnd,29:4:r,24:4:n');
INSERT INTO signature_waves VALUES (44, 1, 1, '101:4:wns');
-- 45 - Forgotten Core Assembly Hall
INSERT INTO signature_waves VALUES (45, 1, 0, '33:6,30:5:wd,24:3:n,23:3:wnd,25:3:rt,26:1:wndR');
INSERT INTO signature_waves VALUES (45, 2, 0, '28:6:wnd,24:3:n,23:2:wnd,25:1:rt');
INSERT INTO signature_waves VALUES (45, 3, 0, '29:6:r,24:3:n,23:2:wnd,25:2:rt');
INSERT INTO signature_waves VALUES (45, 4, 0, '30:10:wd,27:6:w,26:6:wnd');
INSERT INTO signature_waves VALUES (45, 1, 1, '101:4:wns');
-- 46 - Forgotten Core Circuitry Disassembler
INSERT INTO signature_waves VALUES (46, 1, 0, '22:3,33:4,30:9:wd,31:9:nr,32:9:wndt,26:1:wnd');
INSERT INTO signature_waves VALUES (46, 2, 0, '32:4:wnd,27:7:w,28:7:wnd,29:7:rt');
INSERT INTO signature_waves VALUES (46, 3, 0, '30:5:wd,23:3:wnd,24:3:n,25:3:r,26:1:wndt');
INSERT INTO signature_waves VALUES (46, 4, 0, '30:4:wd,31:4:nr,27:4:w,28:4:wnd,29:4:r,23:2:wnd,24:2:n,25:2:r,26:3:wnd');
INSERT INTO signature_waves VALUES (46, 1, 1, '101:4:wns');
-- 47 - Unsecured Core Backup Array
INSERT INTO signature_waves VALUES (47, 1, 0, '22:3,33:3,30:10:wd,24:3:n,23:2:wnd,25:2:rt,26:1:wndR');
INSERT INTO signature_waves VALUES (47, 2, 0, '29:6:r,23:3:wnd,24:3:n,25:2:rt');
INSERT INTO signature_waves VALUES (47, 3, 0, '29:4:r,23:3:wnd,24:3:n,25:3:rt');
INSERT INTO signature_waves VALUES (47, 4, 0, '30:10:wd,27:8:w,26:6:wnd');
INSERT INTO signature_waves VALUES (47, 1, 1, '101:4:wns');
-- 48 - Unsecured Core Emergence
INSERT INTO signature_waves VALUES (48, 1, 0, '22:4,33:4,30:9:wd,31:9:nr,32:9:wndt,26:1:wndR');
INSERT INTO signature_waves VALUES (48, 2, 0, '9:4:n,27:7:w,28:7:wnd,29:7:rt');
INSERT INTO signature_waves VALUES (48, 3, 0, '30:5:wd,23:3:wnd,24:3:n,25:3:r,26:1:wndt');
INSERT INTO signature_waves VALUES (48, 4, 0, '30:4:wd,31:4:nr,27:4:w,28:4:wnd,29:4:r,23:2:wnd,24:2:n,25:2:r,26:1:wndR');
INSERT INTO signature_waves VALUES (48, 1, 1, '101:4:wns');

-- ore sites
INSERT INTO signature_waves VALUES (49, 1, 0, '5:1,8:3'); -- Average Frontier Deposit
INSERT INTO signature_waves VALUES (50, 1, 0, '8:5'); -- Common Perimeter Deposit
INSERT INTO signature_waves VALUES (51, 1, 0, '23:1'); -- Exceptional Core Deposit
INSERT INTO signature_waves VALUES (52, 1, 0, '16:2'); -- Infrequent Core Deposit
INSERT INTO signature_waves VALUES (53, 1, 0, '6:1:n,8:2'); -- Isolated Core Deposit
INSERT INTO signature_waves VALUES (54, 1, 0, '8:5'); -- Ordinary Perimeter Deposit
INSERT INTO signature_waves VALUES (55, 1, 0, '23:1:wnd,27:2:wn'); -- Rarified Core Deposit
INSERT INTO signature_waves VALUES (56, 1, 0, '5:2'); -- Unusual Core Deposit
INSERT INTO signature_waves VALUES (57, 1, 0, '9:2:n'); -- Uncommon Core Deposit
INSERT INTO signature_waves VALUES (58, 1, 0, '10:1,8:2,9:2'); -- Unexceptional Frontier Deposit

-- gas sites
INSERT INTO signature_waves VALUES (59, 1, 0, '8:6,9:4:n'); -- Barren Perimeter Reservoir
INSERT INTO signature_waves VALUES (60, 1, 0, '19:8:w,16:4'); -- Bountiful Frontier Reservoir
INSERT INTO signature_waves VALUES (61, 1, 0, '23:4:wnd'); -- Instrumental Core Reservoir
INSERT INTO signature_waves VALUES (62, 1, 0, '5:4'); -- Minor Perimeter Reservoir
INSERT INTO signature_waves VALUES (63, 1, 0, '11:5'); -- Ordinary Perimeter Reservoir
INSERT INTO signature_waves VALUES (64, 1, 0, '8:6,9:6:n'); -- Sizeable Perimeter Reservoir
INSERT INTO signature_waves VALUES (65, 1, 0, '10:4:w,6:2:n'); -- Token Perimeter Reservoir
INSERT INTO signature_waves VALUES (66, 1, 0, '16:4,17:4:wn'); -- Vast Frontier Reservoir
INSERT INTO signature_waves VALUES (67, 1, 0, '31:4:nr,24:4:n'); -- Vital Core Reservoir


-- Epicenters
INSERT INTO signature_waves VALUES (70, 1, 0, '16:1,19:2');
INSERT INTO signature_waves VALUES (71, 1, 0, '16:1,19:2');
INSERT INTO signature_waves VALUES (72, 1, 0, '16:1,19:2');
INSERT INTO signature_waves VALUES (73, 1, 0, '16:1,19:2');
INSERT INTO signature_waves VALUES (74, 1, 0, '16:1,19:2');
INSERT INTO signature_waves VALUES (75, 1, 0, '16:1,19:2');
INSERT INTO signature_waves VALUES (76, 1, 0, '16:1,19:2');
-- Thera sites
INSERT INTO signature_waves VALUES (77, 1, 0, '16:1,19:2'); -- Epicenter, Thera
INSERT INTO signature_waves VALUES (78, 1, 0, '16:1,19:2'); -- Expedition Command Outpost Wreck
INSERT INTO signature_waves VALUES (79, 1, 0, '16:1,19:2'); -- Planetary Colonization Office Wreck
INSERT INTO signature_waves VALUES (80, 1, 0, '16:1,19:2'); -- Testing Facilities