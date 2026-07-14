# Cardex
I'm building this app because I'm unsatisfied with existing card tracking solutions. 
I want to be able to take photos of my cards and have them tracked automatically. 
I also want to be able to take photos of a binder of cards and have that uploaded automatically.

# How it works
Right now cards need to be on a plain background.
The app uses a homography to warp the image so that the card fills a 300x400 box.
The warped image is then passed into a VGG16 feature extractor and the feature is pickled and saved. 
We compare these features to see if the cards are the same.

# Setup
Create config file and insert api key, you can get this from [pokemontcg.io](https://pokemontcg.io/)
```bash
cp config.ini.example config.ini
```

# Running

```bash
docker compose up -d --build
```

# TODO
- [x] Explore all cards released
- [x] Wishlist cards
- [x] Scan your cards in and have them automatically classified
- [ ] Resolve false negative/positive matches
- [ ] Scan a binder of cards in
- [ ] Create decks of cards
- [ ] Create splat of the card videos that are uploaded 
