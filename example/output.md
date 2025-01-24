`spark.CustomErrorPages#existsFor:42`
```java
/**
 * Holds the custom error pages. A page can be defined as a String or a Route.
 * Note that this class is always used statically therefore custom error pages will
 * be shared between different instances of the Service class.
 */
public class CustomErrorPages {
    /**
     * Verifies that a custom error page exists for the given status code
     * @param status
     * @return true if error page exists
     */
public static boolean existsFor(int status) {
    // ...
        return CustomErrorPages.getInstance().customPages.containsKey(status);
```

`spark.http.matching.GeneralError#modify:59`
```java
/**
 * Modifies the HTTP response and body based on the provided exception and request/response wrappers.
 */
final class GeneralError {
    /**
     * Modifies the HTTP response and body based on the provided exception.
     */
static void modify(HttpServletRequest httpRequest,
                       HttpServletResponse httpResponse,
                       Body body,
                       RequestWrapper requestWrapper,
                       ResponseWrapper responseWrapper,
                       ExceptionMapper exceptionMapper,
                       Exception e) {
    // ...
            if (CustomErrorPages.existsFor(500)) {
```

`spark.http.matching.MatcherFilter#doFilter:143`
```java
/**
 * Matches Spark routes and filters.
 *
 * @author Per Wendel
 */
public class MatcherFilter implements Filter {
@Override
    public void doFilter(ServletRequest servletRequest,
                         ServletResponse servletResponse,
                         FilterChain chain) throws IOException, ServletException {
    // ...
                GeneralError.modify(
```

`spark.embeddedserver.jetty.JettyHandler#doHandle:50`
```java
/**
 * Simple Jetty Handler
 *
 * @author Per Wendel
 */
public class JettyHandler extends SessionHandler {
@Override
    public void doHandle(
            String target,
            Request baseRequest,
            HttpServletRequest request,
            HttpServletResponse response) throws IOException, ServletException {
    // ...
        filter.doFilter(wrapper, response, null);
```

```
org.eclipse.jetty.server.session.SessionHandler.doScope(SessionHandler.java:1598))
No file found ending with 'org/eclipse/jetty/server/session/SessionHandler.java'
```

```
org.eclipse.jetty.server.handler.ScopedHandler.handle(ScopedHandler.java:141))
No file found ending with 'org/eclipse/jetty/server/handler/ScopedHandler.java'
```

```
org.eclipse.jetty.server.handler.HandlerWrapper.handle(HandlerWrapper.java:127))
No file found ending with 'org/eclipse/jetty/server/handler/HandlerWrapper.java'
```

```
org.eclipse.jetty.server.Server.handle(Server.java:516))
No file found ending with 'org/eclipse/jetty/server/Server.java'
```

```
org.eclipse.jetty.server.HttpChannel.lambda$handle$1(HttpChannel.java:487))
No file found ending with 'org/eclipse/jetty/server/HttpChannel.java'
```

```
org.eclipse.jetty.server.HttpChannel.dispatch(HttpChannel.java:732))
No file found ending with 'org/eclipse/jetty/server/HttpChannel.java'
```

```
org.eclipse.jetty.server.HttpChannel.handle(HttpChannel.java:479))
No file found ending with 'org/eclipse/jetty/server/HttpChannel.java'
```

```
org.eclipse.jetty.server.HttpConnection.onFillable(HttpConnection.java:277))
No file found ending with 'org/eclipse/jetty/server/HttpConnection.java'
```

```
org.eclipse.jetty.io.AbstractConnection$ReadCallback.succeeded(AbstractConnection.java:311))
No file found ending with 'org/eclipse/jetty/io/AbstractConnection.java'
```

```
org.eclipse.jetty.io.FillInterest.fillable(FillInterest.java:105))
No file found ending with 'org/eclipse/jetty/io/FillInterest.java'
```

```
org.eclipse.jetty.io.ChannelEndPoint$1.run(ChannelEndPoint.java:104))
No file found ending with 'org/eclipse/jetty/io/ChannelEndPoint.java'
```

```
org.eclipse.jetty.util.thread.QueuedThreadPool.runJob(QueuedThreadPool.java:883))
No file found ending with 'org/eclipse/jetty/util/thread/QueuedThreadPool.java'
```

```
org.eclipse.jetty.util.thread.QueuedThreadPool$Runner.run(QueuedThreadPool.java:1034))
No file found ending with 'org/eclipse/jetty/util/thread/QueuedThreadPool.java'
```

```
java.lang.Thread.run(Thread.java:750))
No file found ending with 'java/lang/Thread.java'
```

---

`spark.CustomErrorPages#add:99`
```java
/**
 * Holds the custom error pages. A page can be defined as a String or a Route.
 * Note that this class is always used statically therefore custom error pages will
 * be shared between different instances of the Service class.
 */
public class CustomErrorPages {
    /**
     * Add a custom error page as a Route handler
     * @param status
     * @param route
     */
static void add(int status, Route route) {
    // ...
        CustomErrorPages.getInstance().customPages.put(status, route);
```

`spark.Service#internalServerError:483`
```java
/**
 * Represents a Spark server "session".
 * If a user wants multiple 'Sparks' in his application the method {@link Service#ignite()} should be statically
 * imported and used to create instances. The instance should typically be named so when prefixing the 'routing' methods
 * the semantic makes sense. For example 'http' is a good variable name since when adding routes it would be:
 * Service http = ignite();
 * ...
 * http.get("/hello", (q, a) {@literal ->} "Hello World");
 */
public final class Service extends Routable {
    /**
     * Maps 500 internal server errors to the provided route.
     */
public synchronized void internalServerError(Route route) {
    // ...
        CustomErrorPages.add(500, route);
```

`spark.Spark#internalServerError:1277`
```java
/**
 * The main building block of a Spark application is a set of routes. A route is
 * made up of three simple pieces:
 * <ul>
 * <li>A verb (get, post, put, delete, head, trace, connect, options)</li>
 * <li>A path (/hello, /users/:name)</li>
 * <li>A callback (request, response)</li>
 * </ul>
 * Example:
 * get("/hello", (request, response) -&#62; {
 * return "Hello World!";
 * });
 * The public methods and fields in this class should be statically imported for the semantic to make sense.
 * Ie. one should use:
 * 'post("/books")' without the prefix 'Spark.'
 *
 * @author Per Wendel
 */
public class Spark {
    /**
     * Maps 500 internal server errors to the provided route.
     */
public static void internalServerError(Route route) {
    // ...
        getInstance().internalServerError(route);
```

`spark.customerrorpages.CustomErrorPagesTest#setup:45`
```java
public class CustomErrorPagesTest {
@BeforeClass
    public static void setup() throws IOException {
    // ...
        internalServerError((request, response) -> {
```

```
sun.reflect.NativeMethodAccessorImpl.invoke0(Native)
Invalid file:line format in line: sun.reflect.NativeMethodAccessorImpl.invoke0(Native)
```

```
Method))
Invalid line format: Method))
```

```
sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62))
No file found ending with 'sun/reflect/NativeMethodAccessorImpl.java'
```

```
sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43))
No file found ending with 'sun/reflect/DelegatingMethodAccessorImpl.java'
```

```
java.lang.reflect.Method.invoke(Method.java:498))
No file found ending with 'java/lang/reflect/Method.java'
```

