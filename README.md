<a href="https://pairamid.com">
  <img src="https://pairamid.com/static/media/pairamid-hero.a6ac0e71.png" width="720px">
</a>

Pairamid-Api provides the backend for [pairamid.com](https://pairamid.com). A web application to facilitate optimal pair programming, team collaboration, and situational awareness. The backend supports both api and websocket requests. Key metrics tracked:

- pair frequency
- cross functional metrics
- pair duration
- pair history
- pair feedback

## Screenshots

<a href="https:/pairamid.com"><img alt="Pairamid Home" src="https://pairamid.com/static/media/duration.6c7fb264.png" width="720px"></a>

<a href="https:/pairamid.com"><img alt="Pairamid Home" src="https://pairamid.com/static/media/history.e41299f9.png" width="720px"></a>

<a href="https:/pairamid.com"><img alt="Pairamid Home" src="https://pairamid.com/static/media/pair_frequency.09fda461.png" width="720px"></a>

## Development

This project was bootstrapped with [Flask](https://github.com/pallets/flask).

 This application bas been built to run with with the react frontend [pairamid-dom](https://github.com/erikolsen/pairamid-dom).

To start local development:

1. pip install -r requirements.txt
1. docker pull postgresql
1. docker run --rm --name pg-pairamid -e POSTGRES_PASSWORD=docker -d -p 5432:5432 postgres 
1. flask add-users
1. flask add-pairs
1. flask run
