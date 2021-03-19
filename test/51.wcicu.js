'use strict';
const Database = require('../.');

describe('wcicu', function () {
    beforeEach(function () {
        this.timeout(99999999);
        const db = this.db = new Database(":memory:");
        db.prepare(`CREATE VIRTUAL TABLE t1 USING fts5(a, tokenize='wcicu zh_CN' );`).run();
        let n = 100;
        let prepare = db.prepare(`insert into t1 (a)
                                  values (?)`);
        let now = Date.now();
        for (let i = 0; i < n; i++) {
            db.transaction(() => {
                for (const data of datas) {
                    prepare.run([`${n}${data}`]);
                }
            })()
            // console.log(i, Date.now() - now);
        }
        console.log('wcicu', 'inserted ', db.prepare('select count(1) as a from t1').get(), 'time:', Date.now() - now, 'ms');
    });
    afterEach(function () {
        this.db.close();
    });

    it('should match', function () {
        this.timeout(99999999);
        const db = this.db;

        function check(s, has, log = false) {
            /**
             * @type {{a:string}[]}
             */
            let now = Date.now();
            let res = db.prepare(`select a
                                  from t1
                                  where a match '"' || ? || '"'`).all([s]);
            log && console.log(s, res);
            console.log('keyword:', s, 'time:', Date.now() - now, 'ms', 'count:', res.length);
            if (!res) {
                throw 'error: res is null';
            }
            if (has ? res.length <= 0 : res.length > 0) {
                throw `error: res should ${has ? '' : 'not '} has result, ${s}`;
            }
            // if (!res.every(e => e.a.toLowerCase().includes(s.toLowerCase()))) {
            //     throw res.find(e => !e.a.includes(s)).a + ' not includes ' + s;
            // }
        }

        check('1', true, false);
        check('断网', true, false);
        check('邀请', true);
        check('载不能取消', true);
        check('消息多端同步', true);
        check('messages', true, false);
        check('MESSAGES', true, false);
        check('BUNDLES', true, false);
        check('v2/messages/delMsg', true, false);
        check('/v1/app/aaa', false, false);
        check('1.4.18.11', true, false);
        check('%', true, false);
        check('@', true, false);
    });
});
describe('trigram', function () {
    beforeEach(function () {
        this.timeout(99999999);
        this.db = new Database(":memory:");
        const db = this.db;
        let now = Date.now();
        db.prepare(`CREATE VIRTUAL TABLE t1 USING fts5(a, tokenize='trigram case_sensitive 0' );`).run();
        let n = 100;
        let prepare = db.prepare(`insert into t1 (a)
                                  values (?)`);
        for (let i = 0; i < n; i++) {
            db.transaction(() => {
                for (const data of datas) {
                    prepare.run([`${n}${data}`]);
                }
            })()
            // console.log(i, Date.now() - now);
        }
        console.log('trigram', 'inserted ', db.prepare('select count(1) as a from t1').get(), 'time:', Date.now() - now, 'ms');
    });
    afterEach(function () {
        this.db.close();
    });

    it('should match', function () {
        const db = this.db;
        this.timeout(99999999);

        function check(s, has, log = false) {
            /**
             * @type {{a:string}[]}
             */
            let now = Date.now();
            let res = db.prepare(`select a
                                  from t1
                                  where a like ? ESCAPE '&'`).all([`%${s.replace(/([&%])/, "&$1")}%`]);
            log && console.log(s, res);
            console.log('keyword:', s, 'time:', Date.now() - now, 'ms', 'count:', res.length);
            if (!res) {
                throw 'error: res is null';
            }
            if (has ? res.length <= 0 : res.length > 0) {
                throw `error: res should ${has ? '' : 'not '} has result, ${s}`;
            }
            if (!res.every(e => e.a.toLowerCase().includes(s.toLowerCase()))) {
                throw res.find(e => !e.a.includes(s)).a + ' not includes ' + s;
            }
        }

        check('1', true, false);
        check('断网', true, false);
        check('邀请', true);
        check('载不能取消', true);
        check('消息多端同步', true);
        check('messages', true, false);
        check('MESSAGES', true, false);
        check('BUNDLES', true, false);
        check('v2/messages/delMsg', true, false);
        check('/v1/app/aaa', false, false);
        check('1.4.18.11', true, false);
        check('%', true, false);
        check('@', true, false);
    });
});

const datas = [];
