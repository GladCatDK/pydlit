docker run -d --net=host pydlit
sleep 5
TEMP_JOB_ID=$(curl -XPOST -H "Content-Type: application/json" -d @example/example_request.json http://localhost:5001/api/distribute/image | jq -r ".id")
sleep 15
RESULT=$(curl -vf -XGET http://localhost:5001/api/distribute/image/$TEMP_JOB_ID | jq -r ".value")

if [[ "$RESULT" != "FINISHED" ]]; then
echo "Test failed."
exit 1
fi
