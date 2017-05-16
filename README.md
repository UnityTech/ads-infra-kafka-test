## Apache Kafka validator + Kontrol pod

### Overview

This project is a [**Docker**](https://www.docker.com) image packaging
some testing logic along with [**Kontrol**](https://github.com/UnityTech/ads-infra-kontrol).
It is meant to be used as a high-level validation tool for [**Kafka**](https://kafka.apache.org/).

### Lifecycle

The initial state will render the [**telegraf**](https://github.com/influxdata/telegraf)
configuration and include the *statds* input. The machine will then oscillate between
producing a batch of records and consuming it. A MD5 digest is maintained between these
2 states and used to make sure that we got the same records back. Any failure will
automatically reset the machine and log to the statsd *alert* counter.

The configuration is found in the pod annotations and currently supports the following:

- *kafka.unity3d.com/topic*: topic to use to produce/consume records
- *kafka.unity3d.com/brokers*: comma separated broker endpoint list

Right now the logic will feature a simple consumer that tracks its offset (e.g we are not
using any partitioning nor consumer groups). Additional work could be done to extend this
model and include partitioning for instance.

Please note the *kontrol* callback is not used.

### Building the image

Pick a distro and build from the top-level directory. For instance:

```
$ docker build -f alpine-3.5/Dockerfile .
```

### Manifest

```
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: kafka-test
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: kafka
        role: test
      annotations:
        kafka.unity3d.com/topic: test
        kafka.unity3d.com/brokers: kafka.default.svc
        kontrol.unity3d.com/opentsdb: kairosdb.us-east-1.applifier.info
    spec:
      containers:
       - image: registry2.applifier.info:5005/ads-infra-kafka-test-alpine-3.5
         name: test-suite
         imagePullPolicy: Always
         ports:
         - containerPort: 8000
           protocol: TCP
         env:
          - name: NAMESPACE
            valueFrom:
              fieldRef:
                fieldPath: metadata.namespace
```

### Support

Contact olivierp@unity3d.com for more information about this project.