#!/bin/bash

set -e

../../../spike-front/admin/bin/delete-news-posts.js --database-from-env --delete
../../../spike-front/admin/bin/load-news-posts.js $1 --database-from-env
