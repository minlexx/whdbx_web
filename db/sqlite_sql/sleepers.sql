DROP TABLE IF EXISTS sleepers;

CREATE TABLE sleepers (
   id int NOT NULL primary key,
   typeid int,
   wh_class text,
   icon text,
   name text,
   --
   signature int,
   maxspeed int,
   orbit int,
   optimal int,
   --
   shield int,
   armor int,
   hull int,
   --
   res_em int,
   res_therm int,
   res_kin int,
   res_exp int,
   --
   dps_em int,
   dps_therm int,
   dps_kin int,
   dps_exp int,
   --
   loot_acd int,
   loot_nna int,
   loot_sdl int,
   loot_sdai int,
   --
   ability text default null
);

-- http://playground.schildwall.info/basics/npcattributes/
-- http://playground.schildwall.info/basics/types/types.php?typeID=30201  "Details for Awakened Watchman"

-- class 1 and class 2 sleepers
INSERT INTO sleepers VALUES (1,  30188, '1,2', 'battleship', 'Sleepless Patroller', 400,735,19000,45000,   0,20000,10000, 75,75,75,75, 56,56,59,59,   0,2,7,0, NULL);
INSERT INTO sleepers VALUES (2,  30189, '1,2', 'battleship', 'Sleepless Watchman',  400,630,65000,105000,  0,12000,6000,  65,65,65,65, 136,136,17,17, 0,2,7,0, NULL);
INSERT INTO sleepers VALUES (3,  30190, '1,2', 'battleship', 'Sleepless Escort',    400,875,55000,75000,   0,16000,8000,  70,70,70,70, 16,16,75,75,   0,2,7,0, NULL);
INSERT INTO sleepers VALUES (4,  30191, '1,2', 'battleship', 'Sleepless Outguard',  400,1050,15000,135000, 0,25000,12500, 75,75,75,75, 88,88,84,84,  1,2,2,0, 'neut');
INSERT INTO sleepers VALUES (5,  30200, '1,2', 'cruiser', 'Awakened Patroller',  150,1190,15000,30000,  0,5000,2500, 70,70,70,70, 10,10,10,10, 0,0,2,0, NULL);
INSERT INTO sleepers VALUES (6,  30201, '1,2', 'cruiser', 'Awakened Watchman',   150,1400,30000,52500,  0,3500,1750, 50,50,50,50, 10,10,5,5,   0,0,2,0, 'neut');
INSERT INTO sleepers VALUES (7,  '1,2', 'cruiser', 'Awakened Escort',    150, 980,  45000, 4000, 2000, 60,60,60,60, 67500, 22,22,5,5, 0,0,2,0, NULL);
INSERT INTO sleepers VALUES (8,  '1,2', 'frigate', 'Emergent Patroller', 35, 1750,  8139, 1000, 500, 60,60,60,60, 15000, 4,4,5,5, 0,2,0,0, NULL);
INSERT INTO sleepers VALUES (9,  '1,2', 'frigate', 'Emergent Watchman',  35, 1925,  5162, 800, 400, 50,50,50,50, 15000, 2,2,5,5, 0,2,0,0, 'neut');
INSERT INTO sleepers VALUES (10, '1,2', 'frigate', 'Emergent Escort',    35, 2100,  5170, 600, 300, 40,40,40,40, 15000, 5,5,7,7, 0,2,0,0, 'web');
INSERT INTO sleepers VALUES (11, '1,2', 'sentry', 'Sirius', 50, 0, 0, 5000, 2500, 40,40,40,40, 250000, 26,26,0,0, 0,0,0,0, NULL);

-- class 3 and class 4 sleepers
INSERT INTO sleepers VALUES (12, '3,4', 'battleship', 'Sleepless Defender',  400, 920, 19000, 28000, 14000, 65,65,65,65, 60000, 79,79,82,82, 1,4,4,1, NULL);
INSERT INTO sleepers VALUES (13, '3,4', 'battleship', 'Sleepless Upholder',  400, 800, 65000, 16800, 8400, 65,65,65,65, 25000, 191,191,24,24, 1,4,4,1, 'neut');
INSERT INTO sleepers VALUES (14, '3,4', 'battleship', 'Sleepless Preserver', 400, 1080, 55000, 22400, 11200, 70,70,70,70, 95000, 23,23,105,105, 1,4,4,1, 'rr');
INSERT INTO sleepers VALUES (15, '3,4', 'battleship', 'Sleepless Safeguard', 400, 1320, 160000, 35000, 17500, 70,70,70,70, 160000, 124,124,117,117, 4,2,2,1, 'web,neut,dis');
INSERT INTO sleepers VALUES (16, '3,4', 'cruiser', 'Awakened Defender',  150, 1480, 15000, 7000, 3500, 70,70,70,70, 45000, 14,14,14,14, 1,2,2,0, NULL);
INSERT INTO sleepers VALUES (17, '3,4', 'cruiser', 'Awakened Upholder',  150, 1728, 30000, 4900, 2450, 50,50,50,50, 80000, 14,14,7,7, 1,2,2,0, 'web,neut');
INSERT INTO sleepers VALUES (18, '3,4', 'cruiser', 'Awakened Preserver', 150, 1240, 45000, 5600, 2800, 60,60,60,60, 75000, 31,31,7,7, 1,2,2,0, 'rr');
INSERT INTO sleepers VALUES (19, '3,4', 'frigate', 'Emergent Defender',  35, 2160,  6651, 1400, 700, 60,60,60,60, 15000, 6,6,6,6, 0,2,2,0, 'web');
INSERT INTO sleepers VALUES (20, '3,4', 'frigate', 'Emergent Upholder',  35, 2400,  5170, 1120, 560, 50,50,50,50, 15000, 3,3,6,6, 0,2,2,0, 'neut,rr');
INSERT INTO sleepers VALUES (21, '3,4', 'frigate', 'Emergent Preserver', 35, 2600,  5177, 840, 420, 40,40,40,40, 15000, 7,7,9,9, 0,2,2,0, 'web,neut,dis');
INSERT INTO sleepers VALUES (22, '3,4', 'sentry', 'Argos', 50, 0, 0, 7000, 3000, 40,40,40,40, 250000, 37,37,0,0, 0,0,0,0, NULL);

-- class 5 and class 6 sleepers
INSERT INTO sleepers VALUES (23, '5,6', 'battleship', 'Sleepless Sentinel', 400, 1125, 19000, 44000, 22000, 65,65,65,65, 75000, 101,101,105,105, 3,2,2,2, 'web,neut,dis');
INSERT INTO sleepers VALUES (24, '5,6', 'battleship', 'Sleepless Keeper',   400, 945, 65000, 26400, 13200, 65,65,65,65, 160000, 245,245,30,30, 3,2,2,2, 'neut');
INSERT INTO sleepers VALUES (25, '5,6', 'battleship', 'Sleepless Warden',   400, 1305, 55000, 35200, 17600, 70,70,70,70, 55000, 29,29,135,135, 3,2,2,2, 'rr');
INSERT INTO sleepers VALUES (26, '5,6', 'battleship', 'Sleepless Guardian', 400, 1575, 30000, 55000, 27500, 70,70,70,70, 35000, 159,159,150,150, 3,2,2,3, 'web,neut,dis');
INSERT INTO sleepers VALUES (27, '5,6', 'cruiser', 'Awakened Sentinel', 150, 1800, 15000, 11000, 5500, 70,70,70,70, 60000, 18,18,18,18, 2,4,4,0, 'web');
INSERT INTO sleepers VALUES (28, '5,6', 'cruiser', 'Awakened Keeper',   150, 2115, 30000, 7700,  3850, 50,50,50,50, 10000, 18,18,9,9, 2,4,4,0, 'web,neut,dis');
INSERT INTO sleepers VALUES (29, '5,6', 'cruiser', 'Awakened Warden',   150, 1485, 45000, 8800,  4400, 60,60,60,60, 35000, 40,40,9,9, 2,4,4,0, 'rr');
INSERT INTO sleepers VALUES (30, '5,6', 'frigate', 'Emergent Sentinel', 35, 2610,  6657, 2200, 1100, 60,60,60,60, 15000, 8,8,8,8, 0,4,4,0, 'web,dis');
INSERT INTO sleepers VALUES (31, '5,6', 'frigate', 'Emergent Keeper',   35, 2880,  5176, 1760, 880,  45,45,45,45, 15000, 4,4,8,8, 0,4,4,0, 'neut,rr');
INSERT INTO sleepers VALUES (32, '5,6', 'frigate', 'Emergent Warden',   35, 3150,  5184, 1320, 660,  40,40,40,40, 15000, 9,9,12,12, 0,4,4,0, 'web,neut,dis');
INSERT INTO sleepers VALUES (33, '5,6', 'sentry', 'Orthrus', 50, 0, 0, 11000, 5500, 40,40,40,40, 250000, 47,47,0,0, 0,0,0,0, NULL);