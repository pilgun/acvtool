.class Ltool/acv/AcvInstrumentation$2;
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
    .line 284
    iput-object p1, p0, Ltool/acv/AcvInstrumentation$2;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public handleMessage(Landroid/os/Message;)Z
    .locals 3

    .prologue
    .line 287
    iget v0, p1, Landroid/os/Message;->what:I

    packed-switch v0, :pswitch_data_0

    .line 296
    :goto_0
    const/4 v0, 0x0

    return v0

    .line 289
    :pswitch_0
    iget v1, p1, Landroid/os/Message;->arg1:I

    .line 290
    iget-object v0, p1, Landroid/os/Message;->obj:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    .line 291
    iget-object v2, p0, Ltool/acv/AcvInstrumentation$2;->this$0:Ltool/acv/AcvInstrumentation;

    invoke-static {v2, v1, v0}, Ltool/acv/AcvInstrumentation;->access$300(Ltool/acv/AcvInstrumentation;ILjava/lang/String;)V

    goto :goto_0

    .line 287
    nop

    :pswitch_data_0
    .packed-switch 0xb
        :pswitch_0
    .end packed-switch
.end method
