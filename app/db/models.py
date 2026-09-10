class AccessRequest(Base):
    __tablename__ = "access_requests"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        index=True
    )

    requested_role: Mapped[str] = mapped_column(
        String(50),
        default="investigator"
    )

    department: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    reason: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="PENDING",
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )