/* DO NOT EDIT THIS FILE - it is machine generated */
#include <jni.h>
/* Header for class org_apache_trafodion_jdbc_t2_SQLMXClobReader */

#ifndef _Included_org_apache_trafodion_jdbc_t2_SQLMXClobReader
#define _Included_org_apache_trafodion_jdbc_t2_SQLMXClobReader
#ifdef __cplusplus
extern "C" {
#endif
#undef org_apache_trafodion_jdbc_t2_SQLMXClobReader_maxSkipBufferSize
#define org_apache_trafodion_jdbc_t2_SQLMXClobReader_maxSkipBufferSize 8192L
/*
 * Class:     org_apache_trafodion_jdbc_t2_SQLMXClobReader
 * Method:    readChunk
 * Signature: (Ljava/lang/String;JJJLjava/lang/String;Ljava/nio/CharBuffer;)I
 */
JNIEXPORT jint JNICALL Java_org_apache_trafodion_jdbc_t2_SQLMXClobReader_readChunk
  (JNIEnv *, jobject, jstring, jlong, jlong, jlong, jstring, jobject);

#ifdef __cplusplus
}
#endif
#endif
