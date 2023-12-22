from __future__ import annotations
from dataclasses import dataclass
import datetime
import typing_extensions as t


@dataclass
class User:
    id: int
    created_at: datetime.datetime
    username: str
    settings: str


@dataclass
class Profile(User):
    id: int
    created_at: datetime.datetime
    username: str
    settings: str
    videos: t.List[Video]
    comments: t.List[Comment]


@dataclass
class VideoFile:
    filename: str
    mimetype: str
    width: int
    height: int
    duration: float


@dataclass
class Image:
    filename: str
    mimetype: str
    width: int
    height: int


@dataclass
class Video:
    id: int
    created_at: datetime.datetime
    title: str
    description: str
    views: int

    thumbnail: Image
    file: VideoFile
    uploader: User
    comments: t.List[Comment]


@dataclass
class Comment:
    id: int
    author: User
    created_at: datetime.datetime
    editted_at: t.Union[datetime.datetime, None]
    text: str


user = Profile(
    id=133,
    created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
    username="InstrumentManiac",
    settings="{}",
    videos=[
        Video(
            id=115,
            created_at=datetime.datetime(2023, 12, 7, 22, 3, 1, 534613),
            title="UNDERTALE - Home",
            description="Recently develop its simple draw work president season. Sea include edge say fear region especially.\nRather significant billion local. Detail notice such ball pretty agreement.",
            views=455721,
            thumbnail=Image(
                filename="2b2bc597552cdf191e4f5f862ee5e73d268926ffb76a2d9ba17a7ab172781301.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="1875b38a7270d0c60649249292095dcb291d123ec0c97e0d3fa2ee055caaa0e1.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=323.566667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=114,
            created_at=datetime.datetime(2023, 12, 7, 22, 2, 11, 384475),
            title="UNDERTALE - Snowy  | @MoisesNieto",
            description="Around including his difficult stop five total. Quite old benefit how let result. Tree fine along especially media.",
            views=330796,
            thumbnail=Image(
                filename="38bfb52e7fdaeb81f32ce6899ca09fbc5583e8afb55528aac1dfc2700d4d0d51.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="441ee4b06a4e0f2d6c160788d75bcf122dfcd2db3e92dee85addd32f42faf5b0.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=293.533333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=113,
            created_at=datetime.datetime(2023, 12, 7, 22, 1, 17, 899129),
            title="UNDERTALE - Death by Glamour",
            description="Keep happy talk federal. Commercial physical whom.\nCouple book once read southern project. Mean son surface food.",
            views=1185186,
            thumbnail=Image(
                filename="0f49257ce38b09f969ef26a02620db0212688c2a7806556c0380bb9001bd7bab.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="fd5e5224637eae4a7b6190951617820529aac4c9155465b10b4e2368b3354575.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=274.866667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=112,
            created_at=datetime.datetime(2023, 12, 7, 22, 0, 28, 539237),
            title="UNDERTALE - Asgore",
            description="Hope project Mrs bag teach material week. Anything must bad again hundred lot often.\nSoldier interest than performance human mother. Help modern relate century despite.",
            views=1106523,
            thumbnail=Image(
                filename="ab1362b69d313536a0ccf2f6de4d52445d5fa6f524422dd17c5de1e8f3b6e627.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="a10f7d5ad48a1103a5f5e7d7891e7c8aadc5b25cbce1b9af3e656a03e3670a91.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=300.366667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=111,
            created_at=datetime.datetime(2023, 12, 7, 21, 59, 34, 253854),
            title="UNDERTALE - It's Raining Somewhere Else",
            description="Believe popular economic. Staff million most player account clear let.\nFeel difficult between chance condition yeah weight. Help water impact hotel because teacher.",
            views=353650,
            thumbnail=Image(
                filename="8e47bfb20fb31d94e7f548bb52ea4a728b1560d9f2ba505efd95885064a51fd2.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="6162f7eab4183245ae295b400eb80fe61421679b21b8228ce8b3595cbaf13a23.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=207.533333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=110,
            created_at=datetime.datetime(2023, 12, 7, 21, 58, 59, 641897),
            title="UNDERTALE - Memory",
            description="Stuff six score leader lot scene alone. Hundred walk eye then big.\nOccur into school thousand than nearly affect evening.",
            views=293459,
            thumbnail=Image(
                filename="3fbc6b54bf29d631de0f7f69ae8e24249b36a06447217ec3cb22cabb29b0b216.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="c5a8949f734b2e146ce0831791f8fe642bc86cd053e6def6ba4ef8ed2a154046.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=251.033333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=109,
            created_at=datetime.datetime(2023, 12, 7, 21, 58, 21, 68426),
            title="UNDERTALE - Ruins | @MoisesNieto",
            description="Paper chair democratic data. Article final stay focus herself. Shoulder open keep enjoy politics all family bring.\nHit arrive lay thing involve resource back do. Writer tough heavy right figure a.",
            views=147780,
            thumbnail=Image(
                filename="3cea59d6700b32d3cdf442a3767a2a6066b8103622ca9c7bde499b4a6c698160.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="37594f6af715b01fee05a4729398cdffecb9f8c1a2330b2270d4ee5717ef16c7.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=232.4,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=108,
            created_at=datetime.datetime(2023, 12, 7, 21, 57, 39, 886425),
            title="UNDERTALE - Battle Against A True Hero",
            description="Place remain example top possible one wish paper. Nor onto range.",
            views=392483,
            thumbnail=Image(
                filename="b6a237acbb0ab4fb36bd6d0fb8deeb8260a563c6ddba519b26ed04b9e78f90ff.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="4f953365910e917b61ad542bc88d85ba2281e1dda25a23f57d79c856589be300.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=274.666667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=107,
            created_at=datetime.datetime(2023, 12, 7, 21, 56, 52, 100347),
            title="Legend of Zelda - Gerudo Valley",
            description="Determine occur foot along single news detail. Reduce dream want tend. Product try game billion.\nCandidate end program throw run draw finally. Discussion pull prevent.",
            views=276139,
            thumbnail=Image(
                filename="f5e88ef64243223064f04c7e03dd89179d8dc245ea469c62b3d5af1bf2b69d05.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="d47a2f3f2634eb8a9f34cbaa72aa934deb650d3bea6cbeadbc54512db4c8cd67.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=280.433333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=106,
            created_at=datetime.datetime(2023, 12, 7, 21, 56, 1, 845018),
            title="DELTARUNE - Field of Hopes and Dreams",
            description="Student sometimes first wind without and. Able present guy cell protect walk. Whatever move work along suffer appear history.",
            views=213321,
            thumbnail=Image(
                filename="5f31ea48ab8fe3284c47b535d1946b48b4f6769e5233af37befb5550fb26a728.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="9ae4a03f96691c0bd7a9fe7e0f34a6779de23f273514e3eb6980eb3320b123ba.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=312.533333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=105,
            created_at=datetime.datetime(2023, 12, 7, 21, 55, 5, 573297),
            title="Legend of Zelda - Lost Woods",
            description="Much civil reflect clear. Market part while economy. During real property key.\nThe model low city increase. Job decade him remain off fire agree.",
            views=87111,
            thumbnail=Image(
                filename="48d73af5499ab8152c24e8402029e1d238d106c3d4624dbc03a9195cf22e792e.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="5ef5ebf484e72c9c06cbd9c1bea402daa3564b04c03692e864d1588cceaaabdc.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=237.066667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=104,
            created_at=datetime.datetime(2023, 12, 7, 21, 54, 26, 181381),
            title="UNDERTALE - Spider Dance",
            description="Knowledge head commercial moment deal. Conference town agent past yet.\nTotal ready line despite five nature. Development two prepare expect important.",
            views=495155,
            thumbnail=Image(
                filename="fe292654e732930b761091d7cae517d0366147f2a6bca260c400e00587d89989.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="735d24a5022386fe9967934f6bcb3d59a23b2e7e7faf754984cfdc7dda74571e.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=249.566667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=103,
            created_at=datetime.datetime(2023, 12, 7, 21, 53, 42, 953635),
            title="DELTARUNE - Ferris Wheel",
            description="Talk read process throughout strategy seat computer suggest. Recognize not world well beyond movement quickly.\nToward size claim. Society tonight interest heavy relationship present.",
            views=49533,
            thumbnail=Image(
                filename="f148a0c94e09b7e890bfd1b5cfc6bc88343486aed092ede7be74616b0347037c.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="654a950d35f5831c37677a05545954d7e7e2717f415cc8966f0c57c69d4e3ae3.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=264.933333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=102,
            created_at=datetime.datetime(2023, 12, 7, 21, 52, 50, 902115),
            title="UNDERTALE - Ghost Fight",
            description="Newspaper speak yeah sea exactly consider man. Whole land our area another relationship. Course administration long second car win.",
            views=227930,
            thumbnail=Image(
                filename="7a675c96969a4f76baaed44f6597ced54dc529d4dcfec85b7e8dedf4c170e8c6.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="c752616e60264bdba137b851df4adce1829ffbbb4f4742b74d5838913b059cac.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=238.066667,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
        Video(
            id=101,
            created_at=datetime.datetime(2023, 12, 7, 21, 52, 8, 310467),
            title="DELTARUNE - My Castle Town  | @MoisesNieto",
            description="Weight city not item a begin as. Between full medical boy member surface. Simply performance others good rule senior.",
            views=60727,
            thumbnail=Image(
                filename="5da117dfa8062af26508d8d8ca92d5c78aecdebfefbf6912434d8ba292d20d2c.webp",
                mimetype="image/webp",
                width=320,
                height=180,
            ),
            file=VideoFile(
                filename="18ef5b152aa5533325586bb13d035a23f18bf96263f0196a0fe81f03cdb3dc74.mp4",
                mimetype="video/mp4",
                width=1280,
                height=720,
                duration=269.233333,
            ),
            uploader=User(
                id=133,
                created_at=datetime.datetime(2023, 12, 7, 21, 51, 23, 248825),
                username="InstrumentManiac",
                settings="{}",
            ),
            comments=[],
        ),
    ],
    comments=[],
)
