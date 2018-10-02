.class Ltool/acv/AcvInstrumentation$3;
.super Ljava/lang/Object;
.source "acvinstrumentation.java"

# interfaces
.implements Landroid/os/Handler$Callback;


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Ltool/acv/AcvInstrumentation;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Ltool/acv/AcvInstrumentation;


# direct methods
.method constructor <init>(Ltool/acv/AcvInstrumentation;)V
    .locals 0

    .prologue
    .line 301
    iput-object p1, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private appendException(Ljava/lang/String;)V
    .locals 3

    .prologue
    .line 374
    const-string v0, "AcvInstrumentation"

    const-string v1, "appendException: Appending exception"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 376
    :try_start_0
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$600(Ltool/acv/AcvInstrumentation;)Ljava/io/File;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v0

    if-nez v0, :cond_0

    .line 377
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$600(Ltool/acv/AcvInstrumentation;)Ljava/io/File;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/File;->createNewFile()Z

    .line 379
    :cond_0
    new-instance v0, Ljava/io/FileWriter;

    iget-object v1, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v1}, Ltool/acv/AcvInstrumentation;->access$600(Ltool/acv/AcvInstrumentation;)Ljava/io/File;

    move-result-object v1

    const/4 v2, 0x1

    invoke-direct {v0, v1, v2}, Ljava/io/FileWriter;-><init>(Ljava/io/File;Z)V

    .line 380
    new-instance v1, Ljava/io/BufferedWriter;

    invoke-direct {v1, v0}, Ljava/io/BufferedWriter;-><init>(Ljava/io/Writer;)V

    .line 381
    invoke-virtual {v1, p1}, Ljava/io/BufferedWriter;->write(Ljava/lang/String;)V

    .line 382
    invoke-virtual {v1}, Ljava/io/BufferedWriter;->close()V
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_0

    .line 388
    :goto_0
    return-void

    .line 384
    :catch_0
    move-exception v0

    .line 385
    const-string v1, "AcvInstrumentation"

    const-string v2, "appendException: Strange error!"

    invoke-static {v1, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 386
    invoke-virtual {v0}, Ljava/io/IOException;->printStackTrace()V

    goto :goto_0
.end method

.method private generateCoverageReport(Ljava/lang/String;)V
    .locals 6

    .prologue
    .line 333
    new-instance v0, Ljava/io/File;

    iget-object v1, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v1}, Ltool/acv/AcvInstrumentation;->access$400(Ltool/acv/AcvInstrumentation;)Ljava/io/File;

    move-result-object v1

    invoke-direct {v0, v1, p1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 334
    const-string v1, "AcvInstrumentation"

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "generateCoverageReport(): "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v1, v2}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 336
    :try_start_0
    const-string v1, "tool.acv.AcvReporter"

    invoke-static {v1}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v1

    .line 337
    const-string v2, "saveExternalPublicFile"

    const/4 v3, 0x1

    new-array v3, v3, [Ljava/lang/Class;

    const/4 v4, 0x0

    .line 338
    invoke-virtual {v0}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v5

    aput-object v5, v3, v4

    .line 337
    invoke-virtual {v1, v2, v3}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v1

    .line 339
    const/4 v2, 0x0

    const/4 v3, 0x1

    new-array v3, v3, [Ljava/lang/Object;

    const/4 v4, 0x0

    aput-object v0, v3, v4

    invoke-virtual {v1, v2, v3}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_0
    .catch Ljava/lang/ClassNotFoundException; {:try_start_0 .. :try_end_0} :catch_0
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_1
    .catch Ljava/lang/NoSuchMethodException; {:try_start_0 .. :try_end_0} :catch_2
    .catch Ljava/lang/IllegalArgumentException; {:try_start_0 .. :try_end_0} :catch_3
    .catch Ljava/lang/IllegalAccessException; {:try_start_0 .. :try_end_0} :catch_4
    .catch Ljava/lang/reflect/InvocationTargetException; {:try_start_0 .. :try_end_0} :catch_5
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_6

    .line 355
    :goto_0
    return-void

    .line 340
    :catch_0
    move-exception v0

    .line 341
    const-string v1, "Is AcvReporter there?"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0

    .line 342
    :catch_1
    move-exception v0

    .line 343
    const-string v1, "SecurityException"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0

    .line 344
    :catch_2
    move-exception v0

    .line 345
    const-string v1, "NoSuchMethodException"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0

    .line 346
    :catch_3
    move-exception v0

    .line 347
    const-string v1, "IllegalArgumentException"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0

    .line 348
    :catch_4
    move-exception v0

    .line 349
    const-string v1, "IllegalAccessException"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0

    .line 350
    :catch_5
    move-exception v0

    .line 351
    const-string v1, "InvocationTargetException"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0

    .line 352
    :catch_6
    move-exception v0

    .line 353
    const-string v1, "Exception"

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V

    goto :goto_0
.end method

.method private removeDirectory(Ljava/io/File;)V
    .locals 4

    .prologue
    .line 392
    invoke-virtual {p1}, Ljava/io/File;->isDirectory()Z

    move-result v0

    if-eqz v0, :cond_1

    .line 393
    invoke-virtual {p1}, Ljava/io/File;->listFiles()[Ljava/io/File;

    move-result-object v1

    .line 394
    if-eqz v1, :cond_0

    array-length v0, v1

    if-lez v0, :cond_0

    .line 395
    array-length v2, v1

    const/4 v0, 0x0

    :goto_0
    if-ge v0, v2, :cond_0

    aget-object v3, v1, v0

    .line 396
    invoke-direct {p0, v3}, Ltool/acv/AcvInstrumentation$3;->removeDirectory(Ljava/io/File;)V

    .line 395
    add-int/lit8 v0, v0, 0x1

    goto :goto_0

    .line 399
    :cond_0
    invoke-virtual {p1}, Ljava/io/File;->delete()Z

    .line 403
    :goto_1
    return-void

    .line 401
    :cond_1
    invoke-virtual {p1}, Ljava/io/File;->delete()Z

    goto :goto_1
.end method

.method private reportAcvError(Ljava/lang/String;Ljava/lang/Exception;)V
    .locals 2

    .prologue
    .line 359
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "Failed to generate Acv coverage. "

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, "\n"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {p2}, Ljava/lang/Exception;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 360
    const-string v1, "AcvInstrumentation"

    invoke-static {v1, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 361
    const/4 v1, 0x0

    invoke-direct {p0, v1, v0}, Ltool/acv/AcvInstrumentation$3;->sendFinishInstrumentationMsg(ILjava/lang/String;)V

    .line 362
    return-void
.end method

.method private sendFinishInstrumentationMsg(ILjava/lang/String;)V
    .locals 2

    .prologue
    .line 366
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$500(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;

    move-result-object v0

    const/16 v1, 0xb

    invoke-static {v0, v1}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v0

    .line 367
    iput p1, v0, Landroid/os/Message;->arg1:I

    .line 368
    iput-object p2, v0, Landroid/os/Message;->obj:Ljava/lang/Object;

    .line 369
    invoke-virtual {v0}, Landroid/os/Message;->sendToTarget()V

    .line 370
    return-void
.end method


# virtual methods
.method public handleMessage(Landroid/os/Message;)Z
    .locals 2

    .prologue
    .line 304
    iget v0, p1, Landroid/os/Message;->what:I

    packed-switch v0, :pswitch_data_0

    .line 328
    :goto_0
    const/4 v0, 0x0

    return v0

    .line 306
    :pswitch_0
    const-string v0, "AcvInstrumentation"

    const-string v1, "handleMessage: Got MSG_GET_COVERAGE"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 307
    iget-object v0, p1, Landroid/os/Message;->obj:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    .line 308
    invoke-direct {p0, v0}, Ltool/acv/AcvInstrumentation$3;->generateCoverageReport(Ljava/lang/String;)V

    goto :goto_0

    .line 312
    :pswitch_1
    const-string v0, "AcvInstrumentation"

    const-string v1, "handleMessage: Got MSG_REPORT_EXCEPTION"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 313
    iget-object v0, p1, Landroid/os/Message;->obj:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    .line 314
    invoke-direct {p0, v0}, Ltool/acv/AcvInstrumentation$3;->appendException(Ljava/lang/String;)V

    goto :goto_0

    .line 318
    :pswitch_2
    const-string v0, "AcvInstrumentation"

    const-string v1, "handleMessage: Got MSG_REMOVE_REPORT_DIR"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 319
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$3;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$400(Ltool/acv/AcvInstrumentation;)Ljava/io/File;

    move-result-object v0

    invoke-direct {p0, v0}, Ltool/acv/AcvInstrumentation$3;->removeDirectory(Ljava/io/File;)V

    goto :goto_0

    .line 323
    :pswitch_3
    const-string v0, "AcvInstrumentation"

    const-string v1, "handleMessage: Got MSG_FINISH_WRITER_OPERATIONS"

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 324
    const/4 v0, -0x1

    const-string v1, "Instrumentation done!"

    invoke-direct {p0, v0, v1}, Ltool/acv/AcvInstrumentation$3;->sendFinishInstrumentationMsg(ILjava/lang/String;)V

    goto :goto_0

    .line 304
    :pswitch_data_0
    .packed-switch 0x1
        :pswitch_0
        :pswitch_1
        :pswitch_2
        :pswitch_3
    .end packed-switch
.end method
