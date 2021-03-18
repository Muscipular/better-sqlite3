'use strict';
const Database = require('../.');

describe('wcicu', function () {
    beforeEach(function () {
        this.db = new Database(util.next());
    });
    afterEach(function () {
        this.db.close();
    });

    it('should match', function () {
        const db = this.db;
        db.prepare(`CREATE VIRTUAL TABLE t1 USING fts5(a, tokenize='wcicu zh_CN');`).run();
        for (const data of datas) {
            db.prepare(`insert into t1 (a) values (?)`).run([data]);
        }

        function check(s, has, log = false) {
            let res = db.prepare(`select a from t1 where a MATCH ?`).all([s]);
            log && console.log(res);
            if (!res) {
                throw 'error: res is null';
            }
            if (has ? res.length <= 0 : res.length > 0) {
                throw `error: res should ${has ? '' : 'not '} has result, ${s}`;
            }
        }

        check('1', true, false);
        check('断网', true);
        check('邀请', true);
        check('载不能取消', true);
        check('消息多端同步', true);
        check('messages', true);
        check('v2 messages delMsg', true, false);
        check('12*', true, false);
    });
});

const datas = [
];
