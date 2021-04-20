{
  'includes': [ 'common-sqlite.gypi' ],

  'target_defaults': {
    'default_configuration': 'Release',
    'cflags':[
      '-std=c99'
    ],
    'configurations': {
      'Debug': {
        'defines': [ 'DEBUG', '_DEBUG' ],
        'msvs_settings': {
          'VCCLCompilerTool': {
            'RuntimeLibrary': 1, # static debug
          },
        },
      },
      'Release': {
        'defines': [ 'NDEBUG' ],
        'msvs_settings': {
          'VCCLCompilerTool': {
            'RuntimeLibrary': 0, # static release
          },
        },
      }
    },
    'msvs_settings': {
      'VCCLCompilerTool': { 
        'AdditionalOptions': [
          '/utf-8'
        ],
      },
      'VCLibrarianTool': {
      },
      'VCLinkerTool': {
        'GenerateDebugInformation': 'true',
      },
    },
    'conditions': [
      ['OS == "win"', {
        'defines': [
          'WIN32'
        ],
        'conditions': [
          ['target_arch == "ia32"', {
            'variables': {
              'openssl_root%': 'OpenSSL-Win32',
              'icu_root%': 'icu',
            }
          }, 'target_arch == "arm64"', {
            'variables': {
              'openssl_root%': 'OpenSSL-Win64-ARM',
              'icu_root%': 'icu',
            }
          }, {
            'variables': {
              'openssl_root%': 'OpenSSL-Win64',
              'icu_root%': 'icu64',
            }
          }]
        ],
        'link_settings': {
          'libraries': [
            '-llibcrypto.lib',
            '-llibssl.lib',
            # The two libs below are needed for the Electron build to succeed
            '-lws2_32.lib',
            '-lcrypt32.lib',
            '-licudt.lib',
            '-licuin.lib',
            '-licuio.lib',
            '-licutest.lib',
            '-licutu.lib',
            '-licuuc.lib',
          ],
          'library_dirs': [
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/<(openssl_root)',
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/<(icu_root)'
          ]
        }
      },
      'OS == "mac"', {
        'variables': {
          'openssl_root%': '/usr/local/opt/openssl@1.1'
        },
        'link_settings': {
          'libraries': [
            # This statically links libcrypto, whereas -lcrypto would dynamically link it
            '<(openssl_root)/lib/libcrypto.a',
            "<!@(/usr/local/opt/icu4c/bin/icu-config --ldflags)",
          ]
        },
        "cflags": ["<!(/usr/local/opt/icu4c/bin/icu-config --cppflags)"],
        "xcode_settings": {
          "OTHER_CFLAGS": [
            "<!(/usr/local/opt/icu4c/bin/icu-config --cppflags)",
          ],
        },
      },
      { # Linux
        'link_settings': {
          'libraries': [
            '-lcrypto'
          ]
        }
      }]
    ],
  },

  'targets': [
    {
      'target_name': 'action_before_build',
      'type': 'none',
      'hard_dependency': 1,
      'actions': [
        {
          'action_name': 'unpack_sqlite_dep',
          'inputs': [
            './sqlcipher-amalgamation-<@(sqlite_version).tar.gz'
          ],
          'outputs': [
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/sqlite3.c',
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/wcicu_tokenizer.c',
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/wcicu_utils.c',
          ],
          'action': ['python','./extract.py','./sqlcipher-amalgamation-<@(sqlite_version).tar.gz','<(SHARED_INTERMEDIATE_DIR)']
        }
      ],
      'direct_dependent_settings': {
        'include_dirs': [
          '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/',
        ]
      },
    },
    {
      'target_name': 'sqlite3',
      'type': 'static_library',
      "conditions": [
        ["OS == \"win\"", {
          'include_dirs': [
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/',
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/openssl-include/',
            './icu/sources/common/',
            './icu/sources/i18n/'
          ]
        },
        "OS == \"mac\"", {
          'include_dirs': [
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/',
            '>(openssl_root)/include',
            './icu/sources/common/',
            './icu/sources/i18n/'
          ]
        },
        { # linux
          'include_dirs': [
            '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/',
            './icu/sources/common/',
            './icu/sources/i18n/'
          ]
        }]
      ],

      'dependencies': [
        'action_before_build',
#         "./icu/icu-generic.gyp:icudata",
#         "./icu/icu-generic.gyp:icuuc#target",
#         "./icu/icu-generic.gyp:icui18n#target",
      ],
      'sources': [
        '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/sqlite3.c',
        '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/wcicu_tokenizer.c',
        '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/wcicu_utils.c',
      ],
      'direct_dependent_settings': {
        'include_dirs': [
          '<(SHARED_INTERMEDIATE_DIR)/sqlcipher-amalgamation-<@(sqlite_version)/'
        ],
        'defines': [
        'SQLITE_THREADSAFE=2',
        'SQLITE_ENABLE_COLUMN_METADATA',
        'HAVE_USLEEP=1',
        'SQLITE_ENABLE_FTS3',
        'SQLITE_ENABLE_FTS5',
        'SQLITE_ENABLE_JSON1',
        'SQLITE_ENABLE_RTREE',
#         'SQLITE_ENABLE_ICU',
        'SQLITE_HAS_CODEC',
        'SQLITE_TEMP_STORE=2',
        'SQLITE_SECURE_DELETE',
        'SQLITE_ENABLE_DBSTAT_VTAB=1',
#         'SQLITE_DQS=0',
        'SQLITE_LIKE_DOESNT_MATCH_BLOBS',
        'SQLITE_USE_URI=0',
        'SQLITE_DEFAULT_MEMSTATUS=0',
        'SQLITE_OMIT_DEPRECATED',
        'SQLITE_OMIT_GET_TABLE',
        'SQLITE_OMIT_TCL_VARIABLE',
        'SQLITE_OMIT_PROGRESS_CALLBACK',
        'SQLITE_OMIT_SHARED_CACHE',
        'SQLITE_TRACE_SIZE_LIMIT=32',
        'SQLITE_DEFAULT_CACHE_SIZE=-16000',
        'SQLITE_DEFAULT_FOREIGN_KEYS=1',
        'SQLITE_DEFAULT_WAL_SYNCHRONOUS=1',
        'SQLITE_ENABLE_COLUMN_METADATA',
        'SQLITE_ENABLE_UPDATE_DELETE_LIMIT',
        'SQLITE_ENABLE_STAT4',
        'SQLITE_ENABLE_FTS3_PARENTHESIS',
        'SQLITE_ENABLE_FTS3',
        'SQLITE_ENABLE_FTS4',
        'SQLITE_ENABLE_FTS5',
        'SQLITE_ENABLE_JSON1',
        'SQLITE_ENABLE_RTREE',
        'SQLITE_ENABLE_GEOPOLY',
        'SQLITE_INTROSPECTION_PRAGMAS',
        'SQLITE_SOUNDEX',
        ],
      },
      'cflags_cc': [
          '-Wno-unused-value'
      ],
      'defines': [
        '_REENTRANT=1',
        'SQLITE_THREADSAFE=2',
        'SQLITE_ENABLE_COLUMN_METADATA',
        'HAVE_USLEEP=1',
        'SQLITE_ENABLE_FTS3',
        'SQLITE_ENABLE_FTS5',
#         'SQLITE_ENABLE_ICU',
        'SQLITE_ENABLE_JSON1',
        'SQLITE_ENABLE_RTREE',
        'SQLITE_HAS_CODEC',
        'SQLITE_TEMP_STORE=2',
        'SQLITE_SECURE_DELETE',
        'SQLITE_ENABLE_DBSTAT_VTAB=1',
#         'SQLITE_DQS=0',
        'SQLITE_LIKE_DOESNT_MATCH_BLOBS',
        'SQLITE_USE_URI=0',
        'SQLITE_DEFAULT_MEMSTATUS=0',
        'SQLITE_OMIT_DEPRECATED',
        'SQLITE_OMIT_GET_TABLE',
        'SQLITE_OMIT_TCL_VARIABLE',
        'SQLITE_OMIT_PROGRESS_CALLBACK',
        'SQLITE_OMIT_SHARED_CACHE',
        'SQLITE_TRACE_SIZE_LIMIT=32',
        'SQLITE_DEFAULT_CACHE_SIZE=-16000',
        'SQLITE_DEFAULT_FOREIGN_KEYS=1',
        'SQLITE_DEFAULT_WAL_SYNCHRONOUS=1',
        'SQLITE_ENABLE_COLUMN_METADATA',
        'SQLITE_ENABLE_UPDATE_DELETE_LIMIT',
        'SQLITE_ENABLE_STAT4',
        'SQLITE_ENABLE_FTS3_PARENTHESIS',
        'SQLITE_ENABLE_FTS3',
        'SQLITE_ENABLE_FTS4',
        'SQLITE_ENABLE_FTS5',
        'SQLITE_ENABLE_JSON1',
        'SQLITE_ENABLE_RTREE',
        'SQLITE_ENABLE_GEOPOLY',
        'SQLITE_INTROSPECTION_PRAGMAS',
        'SQLITE_SOUNDEX',
      ],
      'export_dependent_settings': [
        'action_before_build',
      ],
    }
  ]
}
