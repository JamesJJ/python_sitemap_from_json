# Sitemap Helper

*This docker container reads data from CMS and serves a valid `/sitemap.xml`*

### What is a sitemap:
https://support.google.com/webmasters/answer/156184

### Supported Environment Variables:

| Name  | Default | Description |
|:--:|:--:|:--|
|`LOG_LEVEL`             | `INFO` | Any log level supported by Python e.g. `DEBUG / INFO / WARN / ERROR`
|`JSON_URL`              | `https://www.example.com/api/xxx/v3/products?size=1000&cnty={0}` | API to GET `app_id` list from. `{0}` will be replaced by capital 2-letter country code/ 
|`BASE_URL`              | `https://www.example.com` | Schema and domain used to generate other addresses
|`APPS_PATH`             | `/apps/{0}` | Path to use for each `app_id`. `{0}` will be replaced with the `app_id`
|`APPS_CHANGE_FREQUENCY` | `weekly` | Change frequency for each `app_id`. `always / daily / weekly / monthly` or any other value supported by the sitemap standard for the `<changefreq>` field
|`APPS_PRIORITY`         | `0.5` | Priority for each `app_id`
|`ADD_PATHS`             | `{0}/,daily,1.0\n{0}/list/desktop,weekly,0.8\n{0}/termofuse,monthly,0.2` |Additional paths to add to the sitemap, one per line. Line separator is *unix* newline "\n". Each line is comma separated: path,change frequency,priority. `{0}` will be replaced with the `BASE_URL`
|`CACHE_TIME` | `3600` | Per country-code: How long to cache the result of GET `JSON_URL` 

### Features:

* Per Country-Code output, using `X-Request-Country-Code` Header
* Result caching: impossible to overload CMS Service
* XML Sitemap output at `GET  :8888/sitemap.xml`
* JSON version/health path at: `GET  :8888/version`
* Compact ~ 70MB docker container
* High performance: Easily does 500+ RPS with an 18KB response (equivilent to more than 8 MBytes/s output data) and less than 64 MB memory footprint

### Other notes:

* This thing is one of many ways to generate a sitemap for example.com .... I'm ok if someone wants to take over this and do something different!


