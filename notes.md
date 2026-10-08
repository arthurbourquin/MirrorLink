
### Mac print bourrin

```sh
for f in "$PWD"/*; do
    if file --mime "$f" | grep -q "text/"; then
        echo "===== $f ====="
        cat "$f"
        echo
    fi
done
```