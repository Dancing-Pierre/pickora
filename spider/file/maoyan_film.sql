# -*- coding: utf-8 -*-
create table maoyan_film
(
    id           int auto_increment primary key,
    movieid      varchar(32)   not null comment '猫眼影片ID',
    name         varchar(255)  null comment '片名',
    detail_url   varchar(255)  null comment '详情页链接',
    poster       varchar(512)  null comment '海报图URL',
    type         varchar(255)  null comment '类型',
    actors       varchar(1024) null comment '主演',
    release_date varchar(32)   null comment '上映时间',
    score        varchar(16)   null comment '评分',
    version_tags varchar(64)   null comment '版本标识(imax2d/3d等)',
    ticket_buy   tinyint       null comment '是否售票中 1是 0否',
    state        tinyint       not null default 1 comment '状态 1在映 0过期',
    crawl_date   date          null comment '最近一次成功采集日期',
    create_time  timestamp     default current_timestamp comment '入库时间',
    update_time  timestamp     default current_timestamp on update current_timestamp comment '更新时间',
    constraint uk_movieid unique (movieid)
) comment '猫眼正在热映电影信息';
