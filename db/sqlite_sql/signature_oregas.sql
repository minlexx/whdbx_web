DROP TABLE IF EXISTS signature_oregas;
CREATE TABLE signature_oregas ( sig_id INT, oregas TEXT );

-- ore sites
INSERT INTO signature_oregas VALUES (49, 'ark:3,bis:3,cro:20,dar:4,gne:5,hed:10,hem:20,jas:10,ker:20,mer:0,omb:15,pla:10,pyr:1,sco:6,spo:10,vel:30'); -- Average Frontier Deposit
INSERT INTO signature_oregas VALUES (50, 'ark:1,bis:1,cro:1,dar:1,gne:1,hed:1,hem:1,jas:1,ker:1,mer:0,omb:1,pla:3,pyr:2,sco:2,spo:2,vel:0'); -- Common Perimeter Deposit
INSERT INTO signature_oregas VALUES (51, 'ark:4,bis:5,cro:5,dar:5,gne:6,hed:7,hem:10,jas:11,ker:12,mer:1,omb:12,pla:10,pyr:10,sco:8,spo:8,vel:11'); -- Exceptional Core Deposit
INSERT INTO signature_oregas VALUES (52, 'ark:2,bis:2,cro:2,dar:4,gne:4,hed:4,hem:4,jas:4,ker:11,mer:1,omb:11,pla:12,pyr:11,sco:13,spo:4,vel:14'); -- Infrequent Core Deposit
INSERT INTO signature_oregas VALUES (53, 'ark:6,bis:6,cro:6,dar:6,gne:6,hed:6,hem:6,jas:6,ker:6,mer:0,omb:6,pla:0,pyr:0,sco:0,spo:6,vel:8'); -- Isolated Core Deposit
INSERT INTO signature_oregas VALUES (54, 'ark:1,bis:1,cro:1,dar:1,gne:1,hed:3,hem:3,jas:3,ker:4,mer:0,omb:5,pla:0,pyr:13,sco:7,spo:1,vel:15'); -- Ordinary Perimeter Deposit
INSERT INTO signature_oregas VALUES (55, 'ark:1,bis:1,cro:1,dar:1,gne:1,hed:2,hem:3,jas:0,ker:4,mer:1,omb:3,pla:0,pyr:1,sco:0,spo:1,vel:0'); -- Rarified Core Deposit
INSERT INTO signature_oregas VALUES (56, 'ark:1,bis:1,cro:1,dar:1,gne:1,hed:1,hem:1,jas:1,ker:4,mer:1,omb:3,pla:0,pyr:0,sco:1,spo:1,vel:0'); -- Unusual Core Deposit
INSERT INTO signature_oregas VALUES (57, 'ark:4,bis:6,cro:2,dar:1,gne:1,hed:6,hem:9,jas:5,ker:7,mer:0,omb:5,pla:5,pyr:5,sco:0,spo:1,vel:6'); -- Uncommon Core Deposit
INSERT INTO signature_oregas VALUES (58, 'ark:1,bis:1,cro:1,dar:1,gne:1,hed:1,hem:1,jas:1,ker:1,mer:0,omb:1,pla:2,pyr:0,sco:0,spo:1,vel:4'); -- Unexceptional Frontier Deposit

-- gas clouds
INSERT INTO signature_oregas VALUES (59, 'c50:12000,c60:6000'); -- Barren Perimeter Reservoir
INSERT INTO signature_oregas VALUES (60, 'c28:20000,c32:4000'); -- Bountiful Frontier Reservoir
INSERT INTO signature_oregas VALUES (61, 'c320:24000,c540:2000'); -- Instrumental Core Reservoir
INSERT INTO signature_oregas VALUES (62, 'c70:12000,c72:6000'); -- Minor Perimeter Reservoir
INSERT INTO signature_oregas VALUES (63, 'c72:12000,c84:6000'); -- Ordinary Perimeter Reservoir
INSERT INTO signature_oregas VALUES (64, 'c50:6000,c84:12000'); -- Sizeable Perimeter Reservoir
INSERT INTO signature_oregas VALUES (65, 'c60:12000,c70:6000'); -- Token Perimeter Reservoir
INSERT INTO signature_oregas VALUES (66, 'c28:4000,c32:20000'); -- Vast Frontier Reservoir
INSERT INTO signature_oregas VALUES (67, 'c320:2000,c540:24000'); -- Vital Core Reservoir
