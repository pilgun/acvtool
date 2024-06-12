.class public Ltool/acv/AcvReceiver;
.super Landroid/content/BroadcastReceiver;
.source "AcvReceiver.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 11
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .locals 0

    .line 15
    invoke-virtual {p2}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object p1

    const-string p2, "ACV"

    .line 16
    invoke-static {p2, p1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    const-string p2, "tool.acv.calculate"

    .line 17
    invoke-virtual {p1, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-eqz p2, :cond_0

    .line 18
    invoke-static {}, Ltool/acv/AcvCalculator;->calculateCoverage()V

    goto :goto_0

    :cond_0
    const-string p2, "tool.acv.snap"

    if-ne p1, p2, :cond_1

    .line 21
    new-instance p1, Ljava/io/File;

    const-string p2, "/sdcard/Download/app.debloat.instrapp"

    invoke-direct {p1, p2}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1}, Ljava/io/File;->mkdirs()Z

    .line 22
    new-instance p1, Ltool/acv/AcvStoring;

    invoke-direct {p1}, Ltool/acv/AcvStoring;-><init>()V

    .line 23
    invoke-virtual {p1}, Ltool/acv/AcvStoring;->saveCoverage()V

    goto :goto_0

    :cond_1
    const-string p2, "tool.acv.flush"

    if-ne p1, p2, :cond_2

    .line 25
    invoke-static {}, Ltool/acv/AcvFlushing;->flush()V

    :cond_2
    :goto_0
    return-void
.end method
