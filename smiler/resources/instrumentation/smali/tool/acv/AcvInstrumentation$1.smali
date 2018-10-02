.class Ltool/acv/AcvInstrumentation$1;
.super Landroid/content/BroadcastReceiver;
.source "acvinstrumentation.java"


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
    .line 250
    iput-object p1, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 5

    .prologue
    const/4 v4, 0x4

    .line 254
    const-string v0, "AcvInstrumentation"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "Broadcast received in the thread: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Thread;->getName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 256
    invoke-virtual {p2}, Landroid/content/Intent;->getExtras()Landroid/os/Bundle;

    move-result-object v0

    .line 257
    if-eqz v0, :cond_0

    .line 258
    iget-object v1, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    const-string v2, "cancelAnalysis"

    const/4 v3, 0x0

    invoke-virtual {v0, v2, v3}, Landroid/os/Bundle;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0

    invoke-static {v1, v0}, Ltool/acv/AcvInstrumentation;->access$002(Ltool/acv/AcvInstrumentation;Z)Z

    .line 261
    :cond_0
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$000(Ltool/acv/AcvInstrumentation;)Z

    move-result v0

    if-eqz v0, :cond_1

    .line 262
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$100(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;

    move-result-object v0

    const/4 v1, 0x3

    invoke-static {v0, v1}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v0

    .line 263
    invoke-virtual {v0}, Landroid/os/Message;->sendToTarget()V

    .line 264
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$100(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;

    move-result-object v0

    invoke-static {v0, v4}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v0

    .line 265
    invoke-virtual {v0}, Landroid/os/Message;->sendToTarget()V

    .line 279
    :goto_0
    return-void

    .line 269
    :cond_1
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$200(Ltool/acv/AcvInstrumentation;)Z

    move-result v0

    if-eqz v0, :cond_2

    .line 270
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 271
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "onstop_coverage_"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-static {v0, v1}, Ljava/lang/String;->valueOf(J)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ".ec"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 272
    iget-object v1, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v1}, Ltool/acv/AcvInstrumentation;->access$100(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;

    move-result-object v1

    const/4 v2, 0x1

    invoke-static {v1, v2}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v1

    .line 273
    iput-object v0, v1, Landroid/os/Message;->obj:Ljava/lang/Object;

    .line 274
    invoke-virtual {v1}, Landroid/os/Message;->sendToTarget()V

    .line 277
    :cond_2
    iget-object v0, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v0}, Ltool/acv/AcvInstrumentation;->access$100(Ltool/acv/AcvInstrumentation;)Landroid/os/Handler;

    move-result-object v0

    invoke-static {v0, v4}, Landroid/os/Message;->obtain(Landroid/os/Handler;I)Landroid/os/Message;

    move-result-object v0

    .line 278
    invoke-virtual {v0}, Landroid/os/Message;->sendToTarget()V

    goto :goto_0
.end method
