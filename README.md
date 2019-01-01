# MediaAnalyzer

## Installation
```sh
sudo apt install python3 git-secret -y
python -m spacy download en fr it es
```

## Usage

### Run the web server
```sh
python -m media_analyzer.app
```

### Pull new tweets
```sh
python -m media_analyzer.core.puller
```

## API management
### Decript API
```sh
git secret reveal
```

### Encript API
```sh
git secret hide
```
