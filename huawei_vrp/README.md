# Huawei NE40E

Rename your qcow2 disk image to conform to the following pattern:

```
huawei_ne40e-<version>.qcow2
or
huawei_ce12800-<version>.qcow2
```

Build the image with:

```
make
```

The resulting image will be tagged as:

```
vrnetlab/huawei_vrp:<platform>-<version>
```

for example, if the qcow2 image is named `huawei_ne40e-8.180.qcow2`, then the image will be tagged as:

```
vrnetlab/huawei_vrp:ne40e-8.180
```
