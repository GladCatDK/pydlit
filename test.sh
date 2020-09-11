docker run -d --net=host pydlit
sleep 5
TEMP_JOB_ID=$(curl -XPOST -H "Content-Type: application/json" -d @example/example_request.json http://localhost:5001/api/distribute/image | jq -r ".id")
sleep 15

RETRIES=20

for i in `seq 1 $RETRIES`;
do
RESULT=$(curl -vf -XGET http://localhost:5001/api/distribute/image/$TEMP_JOB_ID | jq -r ".value")
if [[ "$RESULT" == "FINISHED" ]]; then
echo "Job is $RESULT"
exit 0
fi
if [[ "$RESULT" == "FAILED" ]]; then
echo "Test $RESULT"
exit 1
fi
if [[ "$RESULT" == "QUEUED" || "$RESULT" == "RUNNING" ]]; then
echo "Attempt $i"
echo "Job still $RESULT"
echo "Waiting."
if [[ $i -eq $RETRIES ]]; then
echo "Retries exceeded. Test failed."
exit 1
fi
sleep 5
fi
done