.class public final Ltool/acv/AcvCalculator;
.super Ljava/lang/Object;
.source "AcvCalculator.java"


# static fields
.field private static final TAG:Ljava/lang/String; = "ACV"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 7
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


.method private static printSum([Ljava/lang/reflect/Field;Ljava/lang/String;)V
    .locals 7

    .line 16
    invoke-static {p0}, Ltool/acv/AcvReporterFields;->fieldsToArray([Ljava/lang/reflect/Field;)[[Z

    move-result-object p0

    const/4 v0, 0x0

    const/4 v1, 0x0

    const/4 v2, 0x0

    const/4 v3, 0x0

    .line 19
    :goto_0
    array-length v4, p0

    if-ge v1, v4, :cond_2

    .line 20
    aget-object v4, p0, v1

    array-length v4, v4

    add-int/2addr v3, v4

    const/4 v4, 0x0

    .line 21
    :goto_1
    aget-object v5, p0, v1

    array-length v6, v5

    if-ge v4, v6, :cond_1

    .line 22
    aget-boolean v5, v5, v4

    if-eqz v5, :cond_0

    add-int/lit8 v2, v2, 0x1

    :cond_0
    add-int/lit8 v4, v4, 0x1

    goto :goto_1

    :cond_1
    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    .line 27
    :cond_2
    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string p1, ": covered "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    const-string p1, " out of "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {p0, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "ACV"

    invoke-static {p1, p0}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method


.method public static calculateCoverage()V
    .locals 2

    .line 31
    const-class v0, Ltool/acv/AcvReporter1;

    invoke-virtual {v0}, Ljava/lang/Class;->getFields()[Ljava/lang/reflect/Field;

    move-result-object v0

    const-string v1, "1"

    .line 32
    invoke-static {v0, v1}, Ltool/acv/AcvCalculator;->printSum([Ljava/lang/reflect/Field;Ljava/lang/String;)V
# additional code starts here
