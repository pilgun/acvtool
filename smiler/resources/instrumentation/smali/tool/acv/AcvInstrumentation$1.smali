.class Ltool/acv/AcvInstrumentation$1;
.super Landroid/content/BroadcastReceiver;
.source "AcvInstrumentation.java"


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

    .line 44
    iput-object p1, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 1

    .line 47
    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string p2, "BroadcastReceiver: saveCoverage: "

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-static {}, Ljava/lang/Thread;->currentThread()Ljava/lang/Thread;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/Thread;->getName()Ljava/lang/String;

    move-result-object p2

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p2, " ---------"

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    const-string p2, "ACV"

    invoke-static {p2, p1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    .line 48
    new-instance p1, Ltool/acv/AcvStoring;

    invoke-direct {p1}, Ltool/acv/AcvStoring;-><init>()V

    .line 49
    invoke-virtual {p1}, Ltool/acv/AcvStoring;->saveCoverage()V

    .line 50
    iget-object p1, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {p1}, Ltool/acv/AcvInstrumentation;->access$000(Ltool/acv/AcvInstrumentation;)Landroid/os/Bundle;

    move-result-object p1

    const-string p2, "id"

    const-string v0, "ACV_Instrumentation"

    invoke-virtual {p1, p2, v0}, Landroid/os/Bundle;->putString(Ljava/lang/String;Ljava/lang/String;)V

    .line 51
    iget-object p1, p0, Ltool/acv/AcvInstrumentation$1;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {p1}, Ltool/acv/AcvInstrumentation;->access$000(Ltool/acv/AcvInstrumentation;)Landroid/os/Bundle;

    move-result-object p2

    const/4 v0, -0x1

    invoke-virtual {p1, v0, p2}, Ltool/acv/AcvInstrumentation;->finish(ILandroid/os/Bundle;)V

    return-void
.end method
