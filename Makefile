all: run

run:
	docker-compose up -d
	docker wait ss-scraper-1
	docker-compose down

clean:
	docker-compose rm

