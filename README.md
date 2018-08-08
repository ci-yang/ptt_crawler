# ptt_crawler

PTT crawler with simple clean up.

### How to use

1. pip install -r requirements.txt
2. python crawler.py [board Name]
3. check the json file

### After generate the JSON file

You can process the content of the articles using *Build_Articles_Json.py*

```
python Build_Articles_Json.py [JSON FILE NAME]
```
ex. python Build_Articles_Json.py test.json

this program could generate the processed contents of articles with JSON object structure.