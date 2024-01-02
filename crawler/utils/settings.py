
class CrawlerSettings:

    __settings = {
        "DEBUG_LOCAL":{},
        "DEBUG_SELENIUM":{},
        "SPLASH_LOCAL":{
            "SPLASH_URL": "http://localhost:8050",
            "DOWNLOADER_MIDDLEWARES": {
                "scrapy_splash.SplashCookiesMiddleware": 723,
                "scrapy_splash.SplashMiddleware": 725,
                "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
            },
            # Enable Splash Deduplicate Args Filter
            "SPIDER_MIDDLEWARES": {
                "scrapy_splash.SplashDeduplicateArgsMiddleware": 100,
            },
            # Define the Splash DupeFilter
            "DUPEFILTER_CLASS": "scrapy_splash.SplashAwareDupeFilter",
            "HTTPCACHE_STORAGE": "scrapy_splash.SplashAwareFSCacheStorage",

            "LOG_LEVEL": "INFO"
        },
        "SELENIUM_LOCAL":{
            "SELENIUM_DRIVER_NAME"           : 'chrome',
            "SELENIUM_DRIVER_EXECUTABLE_PATH": "http://localhost:4444/wd/hub",
            "SELENIUM_DRIVER_ARGUMENTS"      : [
                '--no-sandbox',
                '--incognito',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                "--ignore-ssl-errors=yes",
                "--ignore-certificate-errors",
                "--window-size=1920,1080",
                '--allow-running-insecure-content',
                '--disable-logging',
                '--log-level=2',
                '--headless'
            ],
            "DOWNLOADER_MIDDLEWARES"         : {
                'crawlers.courses.middlewares.RemoteSeleniumMiddleware': 800
            },

            "LOG_LEVEL": "INFO"

        }
    }

    @classmethod
    def get(cls, tag="DEBUG_LOCAL"):
        return cls.__settings.get(tag)


