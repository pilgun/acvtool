.class public final Ltool/acv/AcvFlushing;
.super Ljava/lang/Object;
.source "AcvFlushing.java"


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 6
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method private static flushArrays([Ljava/lang/reflect/Field;)V
    .locals 3

    .line 10
    invoke-static {p0}, Ltool/acv/AcvReporterFields;->fieldsToArray([Ljava/lang/reflect/Field;)[[Z

    move-result-object p0

    const/4 v0, 0x0

    const/4 v1, 0x0

    .line 11
    :goto_0
    array-length v2, p0

    if-ge v1, v2, :cond_0

    .line 12
    aget-object v2, p0, v1

    invoke-static {v2, v0}, Ljava/util/Arrays;->fill([ZZ)V

    add-int/lit8 v1, v1, 0x1

    goto :goto_0

    :cond_0
    return-void
.end method


.method public static flush()V
    .locals 1

    .line 18
    const-class v0, Ltool/acv/AcvReporter1;

    invoke-virtual {v0}, Ljava/lang/Class;->getFields()[Ljava/lang/reflect/Field;

    move-result-object v0

    .line 19
    invoke-static {v0}, Ltool/acv/AcvFlushing;->flushArrays([Ljava/lang/reflect/Field;)V
# additional code starts here
