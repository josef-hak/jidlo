FROM python:3.12-slim AS build-data
RUN pip install --no-cache-dir pyyaml pillow
COPY build.py /src/
COPY data/ /src/data/
WORKDIR /src
RUN python build.py

FROM hugomods/hugo:reg AS build-site
COPY hugo.toml /src/
COPY layouts/ /src/layouts/
COPY static/ /src/static/
COPY --from=build-data /src/content /src/content/
COPY --from=build-data /src/static/imgs/food /src/static/imgs/food/
WORKDIR /src
RUN hugo --minify

FROM nginx:alpine
COPY --from=build-site /src/public /usr/share/nginx/html
