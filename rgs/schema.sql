DROP TABLE IF EXISTS presentation;
CREATE TABLE IF NOT EXISTS presentation (
    id integer PRIMARY KEY AUTOINCREMENT,
    title text NOT NULL,
    presenters text NOT NULL,
    scheduled date DEFAULT null,
    time_range text DEFAULT '',
    notes text NOT NULL DEFAULT ''
);
INSERT INTO presentation VALUES (null,'Dynamic Key-Value Memory Networks for Knowledge Tracing','Mohammad','2018-05-21','10-11am','');
INSERT INTO presentation VALUES (null,'Comparison of Indoor Air Quality in Schools: Urban vs. Industrial ''Oil & Gas'' Zones in Kuwait','Dr. Ali Al-Hemoud','2018-05-30','9:30-10am','');
INSERT INTO presentation VALUES (null,'Long-Term Spatiotemporal Analysis of Social Media for Device-to-Device Networks','Muneera & Megha','2018-05-30','10-11am','<a href="https://gist.github.com/mmkhajah/ae2b3421ec4bcb2bd3ecb9a2bf928cdb">The problem with Fig. 1</a>');

DROP TABLE IF EXISTS attachment;
CREATE TABLE attachment (
    id integer primary key autoincrement,
    presentation_id integer not null,
    filename text not null,
    foreign key (presentation_id) references presentation(id)
);
