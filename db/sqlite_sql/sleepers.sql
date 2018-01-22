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
   shield_res_em int,
   shield_res_therm int,
   shield_res_kin int,
   shield_res_exp int,
   --
   armor_res_em int,
   armor_res_therm int,
   armor_res_kin int,
   armor_res_exp int,
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
   ability text default null,
   --
   neut_range int,
   neut_amount int,
   neut_duration,
   --
   dis_range int,
   dis_strength int,
   --
   web_range int,
   web_strength int,
   --
   rr_range int,
   rr_amount int,
   rr_duration int,
   --
   extra_comment text default ''
);

-- http://playground.schildwall.info/basics/npcattributes/
-- http://playground.schildwall.info/basics/types/types.php?typeID=30201  "Details for Awakened Watchman"

-- class 1 and class 2 sleepers
INSERT INTO sleepers VALUES (1,  30188, '1,2', 'battleship', 'Sleepless Patroller', 400,735,19000,45000,   0,20000,10000, 0,0,0,0, 75,75,75,75, 56,56,59,59,   0,2,7,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (2,  30189, '1,2', 'battleship', 'Sleepless Watchman',  400,630,65000,105000,  0,12000,6000,  0,0,0,0, 65,65,65,65, 136,136,17,17, 0,2,7,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (3,  30190, '1,2', 'battleship', 'Sleepless Escort',    400,875,55000,75000,   0,16000,8000,  0,0,0,0, 70,70,70,70, 16,16,75,75,   0,2,7,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (4,  30191, '1,2', 'battleship', 'Sleepless Outguard',  400,1050,15000,135000, 0,25000,12500, 0,0,0,0, 75,75,75,75, 88,88,84,84,  1,2,2,0, 'neut', 25000,100,10, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (5,  30200, '1,2', 'cruiser', 'Awakened Patroller',  150,1190,15000,30000,  0,5000,2500, 0,0,0,0, 70,70,70,70, 10,10,10,10, 0,0,2,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (6,  30201, '1,2', 'cruiser', 'Awakened Watchman',   150,1400,30000,52500,  0,3500,1750, 0,0,0,0, 50,50,50,50, 10,10,5,5,   0,0,2,0, 'neut', 40000,60,10, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (7,  30202, '1,2', 'cruiser', 'Awakened Escort',     150,980,45000,67500,   0,4000,2000, 0,0,0,0, 60,60,60,60, 22,22,5,5, 0,0,2,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (8,  30209, '1,2', 'frigate', 'Emergent Patroller',  35,1750,8000,15000,  0,1000,500, 0,0,0,0, 60,60,60,60, 4,4,5,5, 0,2,0,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (9,  30210, '1,2', 'frigate', 'Emergent Watchman',   35,1925,5000,15000,  0,800,400,  0,0,0,0, 50,50,50,50, 2,2,5,5, 0,2,0,0, 'neut', 7000,30,10, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (10, 30211, '1,2', 'frigate', 'Emergent Escort',     35,2100,5000,15000,  0,600,300, 0,0,0,0, 40,40,40,40, 5,5,7,7, 0,2,0,0, 'web', 0,0,0, 0,0, 10000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (11, 30460, '1,2', 'sentry', 'Vigilant Sentry Tower', 50,0,0,250000, 0,5000,2500, 0,0,0,0, 40,40,40,40, 26,26,0,0, 0,0,0,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');

-- class 3 and class 4 sleepers
INSERT INTO sleepers VALUES (12, 30192, '3,4', 'battleship', 'Sleepless Defender',  400,920,19000,60000, 0,28000,14000, 0,0,0,0, 65,65,65,65, 79,79,82,82, 1,4,4,1, 'web', 0,0,0, 0,0, 30000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (13, 30193, '3,4', 'battleship', 'Sleepless Upholder',  400,800,65000,225000, 0,16800,8400, 0,0,0,0, 65,65,65,65, 191,191,24,24, 1,4,4,1, 'neut', 70000,100,10, 0,0, 0,0, 0,0,0,'');
INSERT INTO sleepers VALUES (14, 30194, '3,4', 'battleship', 'Sleepless Preserver', 400,1080,55000,95000, 0,22400,11200, 0,0,0,0, 70,70,70,70, 23,23,105,105, 1,4,4,1, 'rr', 0,0,0, 0,0, 0,0, 70000,650,10, '');
INSERT INTO sleepers VALUES (15, 30195, '3,4', 'battleship', 'Sleepless Safeguard', 400,1320,150000,255000, 0,35000,17500, 0,0,0,0, 75,80,75,75, 124,124,117,117, 4,2,2,1, 'web,neut,dis', 25000,200,10, 24000,1, 30000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (16, 30203, '3,4', 'cruiser', 'Awakened Defender',  150,1480,15000,45000, 0,7000,3500, 0,0,0,0, 70,70,70,70, 14,14,14,14, 1,2,2,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (17, 30204, '3,4', 'cruiser', 'Awakened Upholder',  150,1728,30000,78750, 0,4900,2450, 0,0,0,0, 50,50,50,50, 14,14,7,7, 1,2,2,0, 'web,neut', 40000,60,10, 0,0, 40000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (18, 30205, '3,4', 'cruiser', 'Awakened Preserver', 150,1240,45000,101250, 0,5600,2800, 0,0,0,0, 60,60,60,60, 31,31,7,7, 1,2,2,0, 'rr', 0,0,0, 0,0, 0,0, 50000,520,10, '');
INSERT INTO sleepers VALUES (19, 30212, '3,4', 'frigate', 'Emergent Defender',  35,2160,6500,15000, 0,1400,700, 0,0,0,0, 60,60,60,60, 6,6,6,6, 0,2,2,0, 'web', 0,0,0, 0,0, 10000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (20, 30213, '3,4', 'frigate', 'Emergent Upholder',  35,2400,5000,15000, 0,1120,560, 0,0,0,0, 50,50,50,50, 3,3,6,6, 0,2,2,0, 'neut,rr', 7000,30,10, 0,0, 0,0, 40000,190,10, '');
INSERT INTO sleepers VALUES (21, 30214, '3,4', 'frigate', 'Emergent Preserver', 35,2600,5000,15000, 0,840,420, 0,0,0,0, 40,40,40,40, 7,7,9,9, 0,2,2,0, 'web,neut,dis', 7000,30,10, 24000,1, 10000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (22, 30461, '3,4', 'sentry', 'Wakeful Sentry Tower', 50,0,0,250000, 0,7000,3500, 0,0,0,0, 40,40,40,40,  37,37,0,0, 0,0,0,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');

-- class 5 and class 6 sleepers
INSERT INTO sleepers VALUES (23, 30196, '5,6', 'battleship', 'Sleepless Sentinel', 400,1125,19000,75000, 0,44000,22000, 0,0,0,0, 65,65,65,65, 101,101,105,105, 3,2,2,2, 'web,neut,dis', 25000,180,10, 24000,1, 30000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (24, 30197, '5,6', 'battleship', 'Sleepless Keeper',   400,945,65000,300000, 0,26400,13200, 0,0,0,0, 65,65,65,65, 245,245,30,30, 3,2,2,2, 'neut', 70000,120,10, 0,0, 0,0, 0,0,0, '');
INSERT INTO sleepers VALUES (25, 30198, '5,6', 'battleship', 'Sleepless Warden',   400,1305,55000,255000, 0,35200,17600, 0,0,0,0, 70,70,70,70, 29,29,135,135, 3,2,2,2, 'rr', 0,0,0, 0,0, 0,0, 77000,730,10, '');
INSERT INTO sleepers VALUES (26, 30199, '5,6', 'battleship', 'Sleepless Guardian', 400,1575,35000,330000, 0,55000,27500, 0,0,0,0, 75,80,75,75, 159,159,150,150, 3,2,2,3, 'web,neut,dis', 40000,360,10, 40000,2, 40000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (27, 30206, '5,6', 'cruiser', 'Awakened Sentinel', 150,1800,15000,60000, 0,11000,5500, 0,0,0,0, 70,70,70,70, 18,18,18,18, 2,4,4,0, 'web', 0,0,0, 0,0, 40000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (28, 30207, '5,6', 'cruiser', 'Awakened Keeper',   150,2115,30000,105000, 0,7700,3850, 0,0,0,0, 50,50,50,50, 18,18,9,9, 2,4,4,0, 'web,neut,dis', 40000,60,10, 40000,1, 40000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (29, 30208, '5,6', 'cruiser', 'Awakened Warden',   150,1485,45000,135000, 0,8800,4400, 0,0,0,0, 60,60,60,60, 40,40,9,9, 2,4,4,0, 'rr', 0,0,0, 0,0, 0,0, 55000,580,10, '');
INSERT INTO sleepers VALUES (30, 30215, '5,6', 'frigate', 'Emergent Sentinel', 35,2610,6500,15000, 0,2200,1100, 0,0,0,0, 60,60,60,60, 8,8,8,8, 0,4,4,0, 'web,dis', 0,0,0, 24000,1, 10000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (31, 30216, '5,6', 'frigate', 'Emergent Keeper',   35,2880,5000,15000, 0,1760,880,  0,0,0,0, 45,45,45,45, 4,4,8,8, 0,4,4,0, 'neut,rr', 7000,30,10, 0,0, 0,0, 44000,260,10, '');
INSERT INTO sleepers VALUES (32, 30217, '5,6', 'frigate', 'Emergent Warden',   35,3150,5000,15000, 0,1320,660,  0,0,0,0, 40,40,40,40, 9,9,12,12, 0,4,4,0, 'web,neut,dis', 7000,30,10, 24000,1, 10000,60, 0,0,0, '');
INSERT INTO sleepers VALUES (33, 30462, '5,6', 'sentry', 'Restless Sentry Tower', 50,0,0,250000, 0,11000,5500, 0,0,0,0, 40,40,40,40, 47,47,0,0, 0,0,0,0, NULL, 0,0,0, 0,0, 0,0, 0,0,0, '');

-- Drifter Battleship
INSERT INTO sleepers VALUES (100, 37473, '5,6', 'drifter_battleship', 'Drifter Response Battleship', 25000,6000,40000,75000, 800000,1200000,150000, 49,20,49,49, 0,50,50,50, 400,400,400,400, 36,30,30,45, 'web,neut,scram', 100000,2000,10, 100000,20, 100000,60, 0,0,0, 'Warp core strength: +3');
INSERT INTO sleepers VALUES (101, 37472, '5,6', 'battleship', 'Upgraded Avenger', 30000,3000,20000,320000, 0,250000,150000, 0,0,0,0, 75,80,75,75, 320,320,320,320, 1,2,2,2, 'web,neut,scram', 100000,1500,20, 100000,15, 100000,50, 0,0,0, 'Capital Escalation Battleship');
